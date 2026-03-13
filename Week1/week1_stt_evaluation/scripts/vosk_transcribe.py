import wave
import json
import os
from vosk import Model, KaldiRecognizer

MODEL_PATH = "../models/vosk-model-small-en-us-0.15"
AUDIO_PATH = "../audio/sample_meeting.wav"
OUTPUT_PATH = "../outputs/vosk_output.txt"

wf = wave.open(AUDIO_PATH, "rb")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, wf.getframerate())

transcript = ""

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        transcript += result.get("text", "") + " "

final_result = json.loads(rec.FinalResult())
transcript += final_result.get("text", "")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(transcript)

print("Vosk transcription saved.")
