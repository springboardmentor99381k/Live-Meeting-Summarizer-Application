import json
import threading
import asyncio
import queue
from datetime import datetime
from fastapi import FastAPI, Request, File, UploadFile
import shutil
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import bcrypt
from bson import ObjectId
import os

from backend import STTDiarizationSummarizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = STTDiarizationSummarizer()
sse_queue = queue.Queue()

# Database Configuration
try:
    mongo_uri = os.environ.get("MONGO_URI", "mongodb_uri")
    
    # Establish connection with robust SSL handling for generalized OS compatibility
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
    db = client["meeting_summarizer"]
    client.server_info()
    print("MongoDB connected successfully.")
except Exception as e:
    print(f"Warning: MongoDB connection failed - {e}")

# Data Models
class UserAuth(BaseModel):
    username: str
    password: str

class StartRequest(BaseModel):
    pass

class SaveSessionRequest(BaseModel):
    user_id: str
    name: str
    duration_minutes: int
    transcript: List[Dict[str, Any]]
    analytics: List[Dict[str, Any]]
    summary: Dict[str, Any]

# Authentication Routes
@app.post("/api/register")
def register(user: UserAuth):
    users_col = db["users"]
    if users_col.find_one({"username": user.username}):
        return {"error": "Username already exists"}
    
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    result = users_col.insert_one({
        "username": user.username,
        "password": hashed_pw
    })
    return {"status": "success", "user_id": str(result.inserted_id)}

@app.post("/api/login")
def login(user: UserAuth):
    users_col = db["users"]
    db_user = users_col.find_one({"username": user.username})
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"]):
        return {"error": "Invalid credentials"}
    return {"status": "success", "user_id": str(db_user["_id"])}

# Session Management Routes
@app.post("/api/sessions")
def save_session(session: SaveSessionRequest):
    sessions_col = db["sessions"]
    result = sessions_col.insert_one({
        "user_id": session.user_id,
        "name": session.name,
        "date": datetime.now().isoformat(),
        "duration_minutes": session.duration_minutes,
        "transcript": session.transcript,
        "analytics": session.analytics,
        "summary": session.summary
    })
    return {"status": "saved", "session_id": str(result.inserted_id)}

@app.get("/api/sessions")
def get_sessions(user_id: str):
    sessions_col = db["sessions"]
    cursor = sessions_col.find({"user_id": user_id}).sort("date", -1)
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    sessions_col = db["sessions"]
    doc = sessions_col.find_one({"_id": ObjectId(session_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
        return doc
    return {"error": "Not found"}

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    sessions_col = db["sessions"]
    result = sessions_col.delete_one({"_id": ObjectId(session_id)})
    if result.deleted_count > 0:
        return {"status": "success", "message": "Session deleted"}
    return {"error": "Not found"}

# Media Processing Routes
@app.post("/api/start")
def start_recording(req: StartRequest):
    if pipeline.is_recording:
        return {"status": "Already recording"}
        
    pipeline.start_recording()
    
    while not sse_queue.empty():
        try:
            sse_queue.get_nowait()
        except queue.Empty:
            break
            
    return {"status": "Started"}

@app.post("/api/upload")
def upload_audio(file: UploadFile = File(...)):
    if pipeline.is_recording:
        return {"status": "Already recording"}
        
    while not sse_queue.empty():
        try:
            sse_queue.get_nowait()
        except queue.Empty:
            break
            
    file_location_raw = "uploaded_audio_raw"
    with open(file_location_raw, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    import subprocess
    subprocess.run(["ffmpeg", "-y", "-i", file_location_raw, "-ar", "16000", "-ac", "1", "-c:a", "pcm_f32le", "-af", "apad=pad_dur=1.5", "uploaded_audio.wav"], capture_output=True)

    def _post_process_upload_worker():
        sse_queue.put({"type": "status", "step": "Transcribing", "message": "Processing uploaded audio..."})
        
        try:
            import soundfile as sf
            wav, sr = sf.read("uploaded_audio.wav")
            duration_minutes = round(len(wav) / sr / 60.0)
        except Exception:
            duration_minutes = 0

        for update in pipeline.run_post_processing("uploaded_audio.wav"):
            if "error" in update:
                sse_queue.put({"type": "error", "message": update["error"]})
            else:
                msg = {"type": "status", "step": update.get("step", ""), "message": update.get("status", "")}
                if "transcript" in update:
                    msg["transcript"] = update["transcript"]
                if "analytics" in update:
                    msg["analytics"] = update["analytics"]
                if "summary" in update:
                    msg["summary"] = update["summary"]
                sse_queue.put(msg)
                
        sse_queue.put({"type": "done", "duration_minutes": duration_minutes})

    threading.Thread(target=_post_process_upload_worker, daemon=True).start()
    return {"status": "Uploaded, processing started"}

@app.post("/api/stop")
def stop_recording():
    if not pipeline.is_recording:
        return {"status": "Not recording"}
        
    def _post_process_worker():
        sse_queue.put({"type": "status", "step": "Transcribing", "message": "Stopping recording & saving audio..."})
        wav_path, duration_minutes = pipeline.stop_recording()
        
        for update in pipeline.run_post_processing(wav_path):
            if "error" in update:
                sse_queue.put({"type": "error", "message": update["error"]})
            else:
                msg = {"type": "status", "step": update.get("step", ""), "message": update.get("status", "")}
                if "transcript" in update:
                    msg["transcript"] = update["transcript"]
                if "analytics" in update:
                    msg["analytics"] = update["analytics"]
                if "summary" in update:
                    msg["summary"] = update["summary"]
                sse_queue.put(msg)
                
        sse_queue.put({"type": "done", "duration_minutes": duration_minutes})

    threading.Thread(target=_post_process_worker, daemon=True).start()
    return {"status": "Stopped, processing started"}

@app.get("/api/stream")
async def stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
                
            if pipeline.is_recording:
                while not pipeline.transcript_queue.empty():
                    text = pipeline.transcript_queue.get_nowait()
                    yield f"data: {json.dumps({'type': 'live_transcript', 'text': text})}\n\n"
            
            while not sse_queue.empty():
                evt = sse_queue.get_nowait()
                yield f"data: {json.dumps(evt)}\n\n"
                
            await asyncio.sleep(0.5)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
