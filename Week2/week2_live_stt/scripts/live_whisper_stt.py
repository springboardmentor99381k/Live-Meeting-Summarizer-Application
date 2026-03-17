import whisper
import sounddevice as sd
import numpy as np
import queue

def transcribe_audio(audio_file=None):
    """
    Week-5 pipeline entry point.
    Uses your existing live microphone STT.
    Returns the combined transcript after you press Ctrl+C.
    """

    model = whisper.load_model("base")
    q = queue.Queue()
    transcript_parts = []

    print("🎤 Start speaking... Press Ctrl+C to stop.")

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    try:
        with sd.InputStream(samplerate=16000, channels=1, callback=callback):
            while True:
                print("\nRecording...")
                audio = q.get()

                audio_np = np.squeeze(audio)

                result = model.transcribe(audio_np)
                print("RAW RESULT:", result)

                text = result.get("text", "").strip()
                if text:
                    print("You said:", text)
                    transcript_parts.append(text)

    except KeyboardInterrupt:
        print("\nStopped Whisper live transcription.")

    # Return full transcript for the pipeline
    return " ".join(transcript_parts)