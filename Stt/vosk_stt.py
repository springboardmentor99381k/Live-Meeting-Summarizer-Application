import wave
import json
import os
from vosk import Model, KaldiRecognizer

# 🔑 Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ Correct model path
MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-en-us-0.15")

def vosk_transcribe(audio_path):
    wf = wave.open(audio_path, "rb")
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())

    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "

    final = json.loads(rec.FinalResult())
    text += final.get("text", "")
    return text.strip()

if __name__ == "__main__":
    audio_file = os.path.join(BASE_DIR, "Data", "sample.wav")
    print(vosk_transcribe(audio_file))