import streamlit as st
import time
import os
from backend.pipeline import submit_task, result
#from utils.audio_recorder import record_audio

# -----------------------------
# SESSION STATE
# -----------------------------
if "recording" not in st.session_state:
    st.session_state.recording = False

# -----------------------------
# FUNCTIONS
# -----------------------------
def start_recording():
    st.session_state.recording = True

def stop_recording():
    st.session_state.recording = False
    st.warning("⚠️ Recording not supported on Streamlit Cloud. Use file upload.")

# -----------------------------
# UI HEADER
# -----------------------------
st.title("🎙️ Meeting AI Assistant")

st.info(f"Status: {result['status']}")

# -----------------------------
# BUTTONS
# -----------------------------
col1, col2 = st.columns(2)

if col1.button("▶ Start Recording"):
    start_recording()

if col2.button("⏹ Stop & Process"):
    stop_recording()

# -----------------------------
# RECORDING STATE
# -----------------------------
if st.session_state.recording:
    st.warning("🎤 Recording in progress... Speak now!")

# -----------------------------
# OUTPUT SECTION (REAL DATA)
# -----------------------------
st.subheader("📝 Transcript")
st.text_area("Transcript", value=result["transcript"], height=150)

st.subheader("👥 Diarized Transcript")
st.text_area("Diarized", value=result["diarized"], height=150)

st.subheader("✨ Summary")
st.success(result["summary"])

# -----------------------------
# PROGRESS BAR
# -----------------------------
progress_map = {
    "Idle": 0,
    "Transcribing...": 30,
    "Diarizing...": 60,
    "Summarizing...": 90,
    "Done": 100
}

st.progress(progress_map.get(result["status"], 0))

# -----------------------------
# FILE UPLOAD (REAL)
# -----------------------------
st.subheader("📂 Upload Audio File")

uploaded_file = st.file_uploader("Upload .wav file", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("▶ Process Uploaded File"):

        os.makedirs("data", exist_ok=True)
        file_path = f"data/{uploaded_file.name}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        submit_task(file_path)

# -----------------------------
# AUTO REFRESH
# -----------------------------
if result["status"] not in ["Idle", "Done"]:
    time.sleep(1)
    st.rerun()# force rebuild
