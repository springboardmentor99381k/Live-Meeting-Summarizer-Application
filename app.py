import os
import time
from datetime import datetime
import streamlit as st
import whisper

from stt.realtime_stt import RealTimeSTT
from pipeline.meeting_pipeline import MeetingPipeline
from utils.exporters import build_markdown, save_markdown_file, save_pdf_file
from utils.mailer import send_summary_email
from utils.logger import save_session_logs

HF_TOKEN = os.getenv("HF_TOKEN")

os.makedirs("outputs/transcripts", exist_ok=True)
os.makedirs("outputs/summaries", exist_ok=True)
os.makedirs("outputs/diarization", exist_ok=True)
os.makedirs("outputs/logs", exist_ok=True)
os.makedirs("outputs/exports", exist_ok=True)
os.makedirs("outputs/uploads", exist_ok=True)

st.set_page_config(page_title="Live Meeting Summarizer", layout="wide")
st.title("🎤 Live Meeting Summarizer")

if "recorder" not in st.session_state:
    st.session_state.recorder = RealTimeSTT(model_name="base")

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

if "live_text" not in st.session_state:
    st.session_state.live_text = ""

if "final_whisper_result" not in st.session_state:
    st.session_state.final_whisper_result = None

if "diarized_transcript" not in st.session_state:
    st.session_state.diarized_transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""

if "markdown_path" not in st.session_state:
    st.session_state.markdown_path = ""

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = ""

meeting_pipeline = MeetingPipeline(HF_TOKEN)
whisper_model = whisper.load_model("base")

meeting_title = st.text_input("Meeting Title", value="Team Meeting")

st.subheader("Choose Input Mode")
input_mode = st.radio(
    "Select source",
    ["Live Recording", "Upload Audio File"],
    horizontal=True
)

def reset_outputs():
    st.session_state.live_text = ""
    st.session_state.final_whisper_result = None
    st.session_state.diarized_transcript = ""
    st.session_state.summary = ""
    st.session_state.transcript_text = ""
    st.session_state.markdown_path = ""
    st.session_state.pdf_path = ""

def save_outputs_and_exports(meeting_title, transcript_text, diarized_transcript, summary):
    transcript_path = "outputs/transcripts/meeting_transcript.txt"
    diarized_path = "outputs/diarization/diarized_transcript.txt"
    summary_path = "outputs/summaries/meeting_summary.txt"

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    with open(diarized_path, "w", encoding="utf-8") as f:
        f.write(diarized_transcript)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_path = f"outputs/exports/{export_timestamp}_meeting_summary.md"
    pdf_path = f"outputs/exports/{export_timestamp}_meeting_summary.pdf"

    markdown_content = build_markdown(
        meeting_title,
        transcript_text,
        diarized_transcript,
        summary
    )

    save_markdown_file(markdown_content, markdown_path)
    save_pdf_file(
        meeting_title,
        transcript_text,
        diarized_transcript,
        summary,
        pdf_path
    )

    st.session_state.markdown_path = markdown_path
    st.session_state.pdf_path = pdf_path

    save_session_logs(
        meeting_title,
        transcript_text,
        diarized_transcript,
        summary
    )

if input_mode == "Live Recording":
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Recording", disabled=st.session_state.is_recording):
            st.session_state.recorder.start_recording()
            st.session_state.is_recording = True
            reset_outputs()

    with col2:
        if st.button("⏹ Stop Recording", disabled=not st.session_state.is_recording):
            st.session_state.is_recording = False

            status = st.status("Processing meeting...", expanded=True)
            with status:
                st.write("Recording stopped.")
                st.write("Transcribing final audio...")

                whisper_result, audio_path = st.session_state.recorder.stop_recording("processed.wav")
                st.session_state.final_whisper_result = whisper_result
                st.session_state.transcript_text = whisper_result.get("text", "")

                st.write("Running diarization...")
                result = meeting_pipeline.run(whisper_result, audio_path)

                st.session_state.diarized_transcript = result["diarized_transcript"]
                st.session_state.summary = result["summary"]

                save_outputs_and_exports(
                    meeting_title,
                    st.session_state.transcript_text,
                    st.session_state.diarized_transcript,
                    st.session_state.summary
                )

                st.write("Completed.")
                status.update(label="Processing complete", state="complete")

    if st.session_state.is_recording:
        st.info("Status: Recording")
        time.sleep(1)
        st.session_state.live_text = st.session_state.recorder.get_live_transcript()
        st.rerun()
    elif st.session_state.final_whisper_result is not None:
        st.success("Status: Summarizing complete")
    else:
        st.warning("Status: Idle")

else:
    uploaded_file = st.file_uploader(
        "Upload meeting audio",
        type=["wav", "mp3", "m4a"]
    )

    if uploaded_file is not None:
        st.audio(uploaded_file)

        if st.button("Process Uploaded Audio"):
            reset_outputs()

            upload_path = os.path.join("outputs/uploads", uploaded_file.name)

            with open(upload_path, "wb") as f:
                f.write(uploaded_file.read())

            status = st.status("Processing uploaded audio...", expanded=True)
            with status:
                st.write("Transcribing uploaded audio...")
                whisper_result = whisper_model.transcribe(upload_path, fp16=False)
                st.session_state.final_whisper_result = whisper_result
                st.session_state.transcript_text = whisper_result.get("text", "")
                st.session_state.live_text = st.session_state.transcript_text

                st.write("Running diarization...")
                result = meeting_pipeline.run(whisper_result, upload_path)

                st.session_state.diarized_transcript = result["diarized_transcript"]
                st.session_state.summary = result["summary"]

                save_outputs_and_exports(
                    meeting_title,
                    st.session_state.transcript_text,
                    st.session_state.diarized_transcript,
                    st.session_state.summary
                )

                st.write("Completed.")
                status.update(label="Processing complete", state="complete")

        if st.session_state.final_whisper_result is not None:
            st.success("Status: Uploaded audio processed")

st.subheader("📝 Real-Time Transcription Log")
st.text_area(
    "Live Transcript",
    value=st.session_state.live_text,
    height=180
)

st.subheader("🧑‍🤝‍🧑 Diarized Transcript")
st.text_area(
    "Diarized Transcript Output",
    value=st.session_state.diarized_transcript,
    height=220
)

st.subheader("📄 Summary")
st.text_area(
    "Meeting Summary",
    value=st.session_state.summary,
    height=180
)

if st.session_state.summary:
    st.subheader("⬇ Export Options")

    if st.session_state.markdown_path and os.path.exists(st.session_state.markdown_path):
        with open(st.session_state.markdown_path, "rb") as f:
            st.download_button(
                "Download Markdown",
                data=f,
                file_name=os.path.basename(st.session_state.markdown_path),
                mime="text/markdown"
            )

    if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
        with open(st.session_state.pdf_path, "rb") as f:
            st.download_button(
                "Download PDF",
                data=f,
                file_name=os.path.basename(st.session_state.pdf_path),
                mime="application/pdf"
            )

    st.subheader("📧 Send via Email")

    sender_email = st.text_input("Sender Email")
    sender_password = st.text_input("App Password", type="password")
    recipient_email = st.text_input("Recipient Email")

    if st.button("Send Email"):
        try:
            send_summary_email(
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_email=recipient_email,
                title=meeting_title,
                summary=st.session_state.summary,
                transcript_path="outputs/transcripts/meeting_transcript.txt",
                markdown_path=st.session_state.markdown_path,
                pdf_path=st.session_state.pdf_path
            )
            st.success("Email sent successfully.")
        except Exception as e:
            st.error(f"Email failed: {e}")