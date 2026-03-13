import whisper

model = whisper.load_model("base")

def whisper_transcribe(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    print(whisper_transcribe("Data/ES2002b.Mix-Headset.wav"))