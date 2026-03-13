import whisper
import re

AUDIO_PATH = "short.wav"

print("Loading Whisper model...")
model = whisper.load_model("medium")

print("Transcribing...")
result = model.transcribe(
    AUDIO_PATH,
    fp16=False,
    language="en",
    temperature=0.0
)

text = result["text"].lower()
text = re.sub(r"[^\w\s]", "", text)
text = re.sub(r"\s+", " ", text)
text = text.strip()

with open("whisper_output.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Whisper transcription completed!")