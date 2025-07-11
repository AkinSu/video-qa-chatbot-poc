import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from keyframe_extractor import KeyFrameExtractor

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
        "message": "Upload and key frame extraction successful.",
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