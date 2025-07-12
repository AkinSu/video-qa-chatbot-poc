import os
import json
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from keyframe_extractor import KeyFrameExtractor
from pydantic import BaseModel

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
KEYFRAMES_DIR = os.getenv("KEYFRAMES_DIR", "keyframes")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KEYFRAMES_DIR, exist_ok=True)

app = FastAPI()

# Initialize key frame extractor
keyframe_extractor = KeyFrameExtractor(FFMPEG_PATH, FFPROBE_PATH)

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(os.getenv("OPENAI_API_KEY"))

class AskRequest(BaseModel):
    video_id: str
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 files are allowed.")
    
    # Save uploaded video
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Extract key frames
    video_name = os.path.splitext(file.filename)[0]
    keyframes_output_dir = os.path.join(KEYFRAMES_DIR, video_name)
    
    extraction_result = keyframe_extractor.extract_keyframes(
        file_location, 
        keyframes_output_dir
    )
    
    # Save extraction metadata
    metadata_file = os.path.join(keyframes_output_dir, "metadata.json")
    os.makedirs(keyframes_output_dir, exist_ok=True)
    with open(metadata_file, "w") as f:
        json.dump(extraction_result, f, indent=2)
    
    return JSONResponse({
        "filename": file.filename,
        "message": f"{video_name} key frames extraction was successful.",
        "keyframe_extraction": extraction_result
    })

@app.get("/keyframes/{video_name}")
async def get_keyframes(video_name: str):
    """
    Get key frame metadata for a specific video
    """
    metadata_file = os.path.join(KEYFRAMES_DIR, video_name, "metadata.json")
    
    if not os.path.exists(metadata_file):
        raise HTTPException(status_code=404, detail="Video not found or no keyframes extracted.")
    
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    return JSONResponse(metadata) 

@app.post("/ask")
async def ask_video_question(req: AskRequest):
    # 1. Load metadata
    metadata_path = os.path.join(KEYFRAMES_DIR, req.video_id, "metadata.json")
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Video metadata not found.")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    timestamps = metadata.get("timestamps", [])

    # 2. Format frame descriptions
    # If no description, use a placeholder
    lines = []
    for ts in timestamps:
        seconds = float(ts.get("timestamp", 0))
        mm = int(seconds // 60)
        ss = int(seconds % 60)
        time_str = f"[{mm:02d}:{ss:02d}]"
        desc = ts.get("description", "No description.")
        lines.append(f"{time_str} {desc}")
    frames_text = "\n".join(lines) if lines else "No frame descriptions available."

    # 3. Build prompt
    prompt = f"""Here are frame descriptions from the video:

{frames_text}

Question: {req.question}
Answer:"""

    # 4. Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant for video understanding."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # 5. Return answer
    return {"answer": answer} 