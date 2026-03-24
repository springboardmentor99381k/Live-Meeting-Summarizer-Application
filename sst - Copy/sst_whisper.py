import whisper

print("Loading Whisper model...")
model = whisper.load_model("base")

print("Transcribing audio...")
result = model.transcribe("test_audio.wav")

print("\nTranscription Result:")
print(result["text"])
