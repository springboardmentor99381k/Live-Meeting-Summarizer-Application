import whisper

def transcribe_audio(audio_file):

    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Running transcription...")
    result = model.transcribe(audio_file)

    segments = []

    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    return segments