import whisper

model = whisper.load_model("base")

print("🔄 Whisper Transcription:")
result = model.transcribe("sample.wav")
print(result["text"])

