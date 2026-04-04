import whisper
from pathlib import Path


def transcribe_audio(audio_file: str) -> dict:
    """Transcribe the given audio file using Whisper.

    Returns a dict with keys: text (full transcript) and segments (timestamped segments).
    """
    try:
        print("Running transcription...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        transcript = result.get("text", "")

        outputs_dir = Path("outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        with open(outputs_dir / "transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        print("Transcription completed")
        return {"text": transcript, "segments": result.get("segments", [])}
    except Exception as e:
        print(f"Transcription failed: {e}")
        return {}
