import threading
import queue
import os

transcript_queue = queue.Queue()


# -----------------------------
# Load transcript from file
# -----------------------------
def load_transcript():
    print("\nLoading transcript...")

    with open("transcript.txt", "r", encoding="utf-8") as f:
        text = f.read()

    transcript_queue.put(text)


# -----------------------------
# Dummy diarization
# -----------------------------
def run_diarization(audio_file):
    print("\nRunning Speaker Diarization...")
    print("Speaker 1")
    print("Speaker 2")

    return ["Speaker 1", "Speaker 2"]


# -----------------------------
# Simple summarization
# -----------------------------
def summarize_text(text):
    print("\nGenerating Summary...")

    summary = text[:200]   # simple summary (first part of text)

    return summary


# -----------------------------
# Pipeline
# -----------------------------
def run_pipeline():

    print("\nStarting backend pipeline...")

    audio_file = "meeting.wav"

    if not os.path.exists(audio_file):
        print("Error: meeting.wav not found")
        return

    # STEP 1: Load transcript in thread
    stt_thread = threading.Thread(target=load_transcript)

    stt_thread.start()
    stt_thread.join()

    transcript = transcript_queue.get()

    print("\nTranscript:")
    print(transcript)

    # STEP 2: Diarization
    speakers = run_diarization(audio_file)

    print("\nSpeakers Detected:")
    print(speakers)

    # STEP 3: Summarization
    summary = summarize_text(transcript)

    print("\nFinal Meeting Summary:")
    print(summary)

    with open("meeting_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    print("\nSummary saved to meeting_summary.txt")