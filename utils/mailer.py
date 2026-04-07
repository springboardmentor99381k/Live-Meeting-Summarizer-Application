import smtplib
from email.message import EmailMessage
from datetime import datetime
import os


def send_summary_email(
    sender_email,
    sender_password,
    recipient_email,
    title,
    summary,
    transcript_path=None,
    markdown_path=None,
    pdf_path=None
):
    msg = EmailMessage()
    subject_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg["Subject"] = f"Meeting Summary – {title}"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    body = f"""Hello,

Please find the meeting summary below.

Title: {title}

Summary:
{summary}

This email was generated automatically by the Live Meeting Summarizer.
"""
    msg.set_content(body)

    for path in [transcript_path, markdown_path, pdf_path]:
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(path)

            if file_name.endswith(".pdf"):
                maintype, subtype = "application", "pdf"
            elif file_name.endswith(".md"):
                maintype, subtype = "text", "markdown"
            else:
                maintype, subtype = "text", "plain"

            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=file_name
            )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)