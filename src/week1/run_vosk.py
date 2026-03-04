import wave
import json
from vosk import Model, KaldiRecognizer

# Path to Vosk model
model_path = "models/vosk-model-small-en-us-0.15"

# Load model
model = Model(model_path)

# Open audio file
wf = wave.open("Data/raw/sample.wav", "rb")

# Create recognizer
rec = KaldiRecognizer(model, wf.getframerate())

text = ""

# Read audio in chunks
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        text += result.get("text", "") + " "

# Final result
final = json.loads(rec.FinalResult())
text += final.get("text", "")

# Save output
with open("transcripts/vosk/sample.txt", "w") as f:
    f.write(text)

print("Vosk transcription completed.")
