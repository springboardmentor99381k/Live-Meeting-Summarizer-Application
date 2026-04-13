from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import uuid

from core.job_manager import create_job
from services.pipeline import process_audio
from utils.file_handler import save_temp_file

router = APIRouter()

@router.post("/process/")
async def process(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())

    create_job(job_id)

    file_path = await save_temp_file(file)

    background_tasks.add_task(process_audio, job_id, file_path)
    print("File received")

    return {"job_id": job_id}

@router.get("/")
def server_starter():
    start_message = "Server has started"
    return start_message