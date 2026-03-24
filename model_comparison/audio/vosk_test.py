import wave
import json
from vosk import Model, KaldiRecognizer

# Open audio file (we are already inside audio/)
wf = wave.open("sample.wav", "rb")

# Load Vosk model (one folder up)
model = Model("../vosk-model-small-en-us-0.22")

rec = KaldiRecognizer(model, wf.getframerate())

print("🔄 Vosk Transcription:")

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        print(result.get("text", ""))

final_result = json.loads(rec.FinalResult())
print(final_result.get("text", ""))

