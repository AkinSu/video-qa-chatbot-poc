import os
import json
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
import faiss
import numpy as np

class FrameContextIndexer:
    def __init__(self, keyframes_dir):
        self.keyframes_dir = keyframes_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # force safetensors path
        self.blip_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            torch_dtype=torch.float32,
            use_safetensors=True
        ).to(self.device)

        # similarly for processor if you want fast transforms
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            use_fast=True
        )
        # CLIP for embeddings
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(self.device)

    def caption_image(self, image_path):
        image = Image.open(image_path).convert('RGB')
        inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        out = self.blip_model.generate(**inputs)
        caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
        return caption

    def embed_text(self, text):
        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            emb = self.clip_model.get_text_features(**inputs)
        return emb.cpu().numpy()[0]

    def process_video(self, video_id):
        frame_dir = os.path.join(self.keyframes_dir, video_id)
        metadata_path = os.path.join(frame_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata not found for video {video_id}")

        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        timestamps = metadata.get("timestamps", [])

        records = []
        for ts in timestamps:
            filename = ts["filename"]
            timestamp = ts["timestamp"]
            frame_path = os.path.join(frame_dir, filename)
            if not os.path.exists(frame_path):
                continue
            caption = self.caption_image(frame_path)
            embedding = self.embed_text(caption)
            records.append({
                "filename": filename,
                "timestamp": timestamp,
                "caption": caption,
                "embedding": embedding.tolist()
            })
        # Save records for later use
        with open(os.path.join(frame_dir, "frame_context.json"), "w") as f:
            json.dump(records, f, indent=2)
        # Build FAISS index
        self.build_faiss_index(video_id, records)
        return records

    def build_faiss_index(self, video_id, records):
        dim = len(records[0]["embedding"])
        index = faiss.IndexFlatL2(dim)
        embeddings = np.array([r["embedding"] for r in records]).astype("float32")
        index.add(embeddings)
        faiss.write_index(index, os.path.join(self.keyframes_dir, video_id, "faiss.index"))

    def query(self, video_id, query_text, top_k=3):
        frame_dir = os.path.join(self.keyframes_dir, video_id)
        context_path = os.path.join(frame_dir, "frame_context.json")
        index_path = os.path.join(frame_dir, "faiss.index")
        if not os.path.exists(context_path) or not os.path.exists(index_path):
            raise FileNotFoundError("Frame context or index not found. Run process_video first.")

        with open(context_path, "r") as f:
            records = json.load(f)
        index = faiss.read_index(index_path)
        query_emb = self.embed_text(query_text).astype("float32").reshape(1, -1)
        D, I = index.search(query_emb, top_k)
        results = [records[i] for i in I[0]]
        return results 