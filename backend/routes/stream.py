# Server sent events

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

from core.job_manager import get_job

router = APIRouter()

async def event_generator(job_id: str):
    last_status = None
    print("SSE CONNECTED", job_id)
    while True:
        job = get_job(job_id)

        if not job:
            yield f"data: {json.dumps({'error':'Invalid job_id'})}\n\n"
            break

        if job["status"] != last_status:
            last_status = job["status"]
            print("CURRENT STATUS:", job["status"])
            yield f"data: {json.dumps(job)}\n\n"

        if job["status"] == "completed":
            break

        await asyncio.sleep(1)

@router.get("/stream/{job_id}")
async def stream(job_id:str):
    print("resonse sent",job_id)
    return StreamingResponse(
        event_generator(job_id),
        media_type="text/event-stream"
    )

# @router.get("/send-email/{job_id}")
# async def send_email(job_id: str):
#     print("Sending")