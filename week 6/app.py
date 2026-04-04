import streamlit as st
import threading
from backend.pipeline import run_pipeline

# Optional: use streamlit-autorefresh if installed
try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_ST_AUTOREFRESH = True
except ImportError:
    _HAS_ST_AUTOREFRESH = False

st.title("Live Meeting Summarizer")

# Initialize shared state container for thread-safe communication
if 'shared_state' not in st.session_state:
    st.session_state.shared_state = {
        "recording": False,
        "transcript": "",
        "diarized_transcript": "",
        "summary": "",
        "status": "Idle",
    }
    st.session_state.pipeline_thread = None

shared_state = st.session_state.shared_state

# Sync shared_state into session_state safely with defaults
st.session_state.recording = shared_state.get("recording", False)
st.session_state.transcript = shared_state.get("transcript", "")
st.session_state.diarized_transcript = shared_state.get("diarized_transcript", "")
st.session_state.summary = shared_state.get("summary", "")
st.session_state.status = shared_state.get("status", "Idle")

# Auto-refresh while recording so UI updates with thread progress
if shared_state.get("recording", False) and _HAS_ST_AUTOREFRESH:
    st_autorefresh(interval=2000, key="refresh_recording")

# Status indicator
st.write(f"Status: {st.session_state.status}")

col1, col2 = st.columns(2)
with col1:
    if st.button("Start Recording"):
        if not shared_state.get("recording", False):
            shared_state["recording"] = True
            shared_state["transcript"] = ""
            shared_state["diarized_transcript"] = ""
            shared_state["summary"] = ""
            shared_state["status"] = "Recording"

            thread = threading.Thread(target=run_pipeline, args=(shared_state,), daemon=True)
            thread.start()
            st.session_state.pipeline_thread = thread

with col2:
    if st.button("Stop Recording"):
        shared_state["recording"] = False
        shared_state["status"] = "Processing"

# Live transcription
st.subheader("Live Transcription")
st.text_area("Live Transcript", value=shared_state.get("transcript", ""), height=150, disabled=True)

# Diarized transcript
st.subheader("Diarized Transcript")
st.text_area("Diarized Transcript", value=shared_state.get("diarized_transcript", ""), height=150, disabled=True)

# Summary
st.subheader("Summary")
st.text_area("Summary", value=shared_state.get("summary", ""), height=150, disabled=True)

# Download buttons
if shared_state.get("diarized_transcript", ""):
    st.download_button("Download Transcript", shared_state.get("diarized_transcript", ""), file_name="transcript.txt")

if shared_state.get("summary", ""):
    st.download_button("Download Summary", shared_state.get("summary", ""), file_name="summary.txt")
