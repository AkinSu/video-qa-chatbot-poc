import os
import json
import requests
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# --- Environment Variable Setup ---
# These URLs will come from your running Colab notebooks
KEYFRAME_EXTRACTOR_URL = os.getenv("KEYFRAME_EXTRACTOR_URL")
FRAME_CONTEXT_URL = os.getenv("FRAME_CONTEXT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check that the URLs and API key are set
if not KEYFRAME_EXTRACTOR_URL or not FRAME_CONTEXT_URL:
    raise RuntimeError("Please set KEYFRAME_EXTRACTOR_URL and FRAME_CONTEXT_URL in your .env file.")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in your .env file.")

# --- FastAPI App Initialization ---
app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)

# Allow all origins for CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    video_id: str
    question: str

# --- API Endpoints ---

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Receives a video file and forwards it to the Keyframe Extractor Colab notebook.
    """
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 files are allowed.")
    
    video_name = os.path.splitext(file.filename)[0]
    video_content = await file.read()
    
    files = {"file": (file.filename, video_content, "video/mp4")}
    try:
        resp = requests.post(f"{KEYFRAME_EXTRACTOR_URL}/extract_keyframes", files=files)
        resp.raise_for_status()
        extraction_result = resp.json()
    except requests.exceptions.RequestException as e:
        print(e)                                  
        raise HTTPException(status_code=500, detail=f"Keyframe extraction service failed: {str(e)}")

    return JSONResponse({
        "filename": file.filename,
        "message": f"Keyframe extraction for {video_name} initiated successfully via Colab.",
        "keyframe_extraction_response": extraction_result
    })

@app.post("/ask")
async def ask_video_question(req: AskRequest):
    """
    This endpoint now needs to fetch frame descriptions from the Frame Context service
    before asking OpenAI.
    """
    # NOTE: This assumes your frame_context notebook has an endpoint to get frame data.
    # We will need to add this endpoint to the colab_notebooks_frame_context.ipynb
    try:
        # Step 1: Get the frame context from the Colab API
        context_resp = requests.get(f"{FRAME_CONTEXT_URL}/frame_context/{req.video_id}")
        context_resp.raise_for_status()
        records = context_resp.json().get("records", [])
        
        # Step 2: Format descriptions
        lines = []
        for record in records:
            seconds = float(record.get("timestamp", 0))
            mm, ss = divmod(int(seconds), 60)
            time_str = f"[{mm:02d}:{ss:02d}]"
            desc = record.get("caption", "No description.")
            lines.append(f"{time_str} {desc}")
        frames_text = "\n".join(lines) if lines else "No frame descriptions available."

        # Step 3: Build prompt and call OpenAI
        prompt = f"""Here are frame descriptions from the video:\n\n{frames_text}\n\nQuestion: {req.question}\nAnswer:"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for video understanding."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not connect to Frame Context service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return {"answer": answer, "context_used": frames_text}

@app.post("/frame_context/{video_id}/index")
async def index_frame_context(video_id: str):
    """Forwards the request to the Frame Context Colab notebook to index a video."""
    try:
        resp = requests.post(f"{FRAME_CONTEXT_URL}/frame_context/{video_id}/index")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return JSONResponse({"error": f"Failed to index frame context: {str(e)}"}, status_code=500)

@app.post("/frame_context/{video_id}/query")
async def query_frame_context(video_id: str, request: Request):
    """Forwards a query to the Frame Context Colab notebook."""
    data = await request.json()
    try:
        resp = requests.post(f"{FRAME_CONTEXT_URL}/frame_context/{video_id}/query", json=data)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return JSONResponse({"error": f"Failed to query frame context: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)