import wave
import json
import vosk

MODEL_PATH = "../../week1_stt_evaluation/models/vosk-model-small-en-us-0.15"
AUDIO_PATH = "ES2002a.Mix-Headset.wav"

print("Loading model...")
model = vosk.Model(MODEL_PATH)

wf = wave.open(AUDIO_PATH, "rb")

rec = vosk.KaldiRecognizer(model, wf.getframerate())

results = []

print("Transcribing audio...")

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        if "text" in result:
            results.append(result["text"])

final_result = json.loads(rec.FinalResult())
if "text" in final_result:
    results.append(final_result["text"])

with open("live_output.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(results))

print("Transcription completed!")