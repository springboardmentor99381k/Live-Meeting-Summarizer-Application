from backend.audio_capture import start_recording, stop_recording
from backend.pipeline import run_pipeline
import time


def record_audio(output_path: str = "meeting.wav", duration_seconds: int = 10):
    # Record audio from the default microphone and save it to a WAV file.
    print("Recording started...")
    start_recording()
    time.sleep(duration_seconds)
    stop_recording(output_path)


def main():
    # 1) Record audio from microphone
    record_audio("meeting.wav", duration_seconds=10)

    # 2) Run the full pipeline (transcribe, diarize, summarize)
    run_pipeline("meeting.wav")


if __name__ == "__main__":
    main()
