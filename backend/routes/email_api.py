from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import markdown
from core.job_manager import get_job
from services.email import send_email

router = APIRouter()


class EmailRequest(BaseModel):
    email: str
    # summary: str
    # transcript: str


@router.post("/send-email/{job_id}")
def send_email_api(job_id: str, req: EmailRequest):

    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not Found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, detail="Processing not finished"
        )  # 400 means bad request(he client (the user/browser) did something wrong.)

    if job.get("email_sent"):
        raise HTTPException(status_code=400, detail="Email already sent")

    result = job["result"]
    summary = result["summary"]
    trascript = "\n".join(result["transcript_lines"])

    summary_html = markdown.markdown(summary)
    trascript_html = "<br>".join(result["transcript_lines"])
    body = f"""
    Meeting Summary

    {summary_html}

    <h2>Diarized Transcript</h2>
    <br>
    {trascript_html}
    """
    send_email(req.email, "Your Meeting Summary", body)
    return {"message": "Email sent successfully"}
