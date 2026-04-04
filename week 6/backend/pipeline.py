import time
import os
from backend.recorder import record_audio
from backend.transcriber import transcribe_chunk
from backend.diarizer import merge_audio_chunks, diarize
from backend.summarizer import summarize

def run_pipeline(state):
    """
    Run the full pipeline: record, transcribe, diarize, summarize.
    Communicate via shared dictionary only (no Streamlit usage).
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    chunk_files = []

    # Ensure defaults are present
    state.setdefault("recording", False)
    state.setdefault("transcript", "")
    state.setdefault("diarized_transcript", "")
    state.setdefault("summary", "")
    state.setdefault("status", "Idle")

    while state.get("recording", False):
        # Record chunk
        chunk_file = os.path.join(temp_dir, f"chunk_{len(chunk_files)}.wav")
        record_audio(duration=5, filename=chunk_file)
        chunk_files.append(chunk_file)

        # Transcribe chunk
        text = transcribe_chunk(chunk_file)
        if not text:
            text = "[No speech detected]"

        state["transcript"] = (state.get("transcript", "") + " " + text).strip()
        state["status"] = "Transcribing"

        # small pause to allow stable IO and avoid jitter
        time.sleep(0.2)

    # After stopping
    state["status"] = "Diarizing"
    merged_file = merge_audio_chunks(chunk_files, os.path.join(temp_dir, "merged.wav"))
    state["diarized_transcript"] = diarize(merged_file)

    state["status"] = "Summarizing"
    state["summary"] = summarize(state.get("diarized_transcript", ""))

    state["status"] = "Completed"

    # Cleanup
    for f in chunk_files + [merged_file]:
        if os.path.exists(f):
            os.remove(f)
