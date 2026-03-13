import whisper

def run_transcription(audio_path):
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Running transcription...")
    result = model.transcribe(audio_path)

    return result["segments"]