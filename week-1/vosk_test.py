import wave
import json
from vosk import Model, KaldiRecognizer

wf = wave.open("amicorpus/EN2001a/audio/EN2001a.Mix-Headset.wav", "rb")

model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, wf.getframerate())

vosk_text = ""

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        vosk_text += result.get("text", "") + " "

final_result = json.loads(rec.FinalResult())
vosk_text += final_result.get("text", "")

with open("vosk_output.txt", "w", encoding="utf-8") as f:
    f.write(vosk_text.lower())

print("Vosk transcription saved.")
