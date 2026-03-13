import whisper

AUDIO_PATH = "../audio/sample_meeting.wav"
OUTPUT_PATH = "../outputs/whisper_output.txt"

model = whisper.load_model("base")
result = model.transcribe(AUDIO_PATH)

text = result["text"]

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("Whisper transcription saved.")
