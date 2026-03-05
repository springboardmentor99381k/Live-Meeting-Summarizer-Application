import whisper

model = whisper.load_model("base")

print("Transcribing...")

result = model.transcribe("Data/raw/sample.wav")

text = result["text"]

print("\n===== TRANSCRIPT =====\n")
print(text)

with open("transcripts/whisper/sample.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("\nSaved successfully.")