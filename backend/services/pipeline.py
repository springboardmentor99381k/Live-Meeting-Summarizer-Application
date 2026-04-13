import asyncio
from core.job_manager import update_job

# from App.backend.services.transcription_diarization import process_speech
from services.transcription_diarization import process_speech
from services.summarization import summarize
# from services.send_email import send_email

async def process_audio(job_id, file_path):

    print("PIPELINE STARTED")
    print("doint transcribing", job_id)
    update_job(job_id, "Transcribing and Diarizing")
    # speech_result = process_speech(file_path)
    speech_result = await asyncio.to_thread(process_speech, file_path)

    print("doint summarizing", job_id)
    update_job(job_id, "summarizing")

    # summary = summarize(speech_result["full_text"])
    summary = await asyncio.to_thread(summarize, speech_result["full_text"])

    result = {
        "transcript_lines": speech_result["lines"],
        "summary": summary
    }
    # result = {
    #     "transcript_lines": ["accccsc",["scsdcccdc"]],
    #     "summary": "It is your summary"
    # }

    update_job(job_id, "completed", result)
    # test
    # print(result)
    # print("job done")
