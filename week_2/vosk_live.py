from vosk import Model, KaldiRecognizer
import json
from audio_stream import start_stream, audio_queue, samplerate

import os
model_path = os.path.join("models", "vosk-model-small-en-us-0.15")
model = Model(model_path)
recognizer = KaldiRecognizer(model, samplerate)

vosk_transcript = []

print("🎙️ Vosk live transcription — Ctrl+C to stop")

with start_stream():
    try:
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print("VOSK:", text)
                    vosk_transcript.append(text)
    except KeyboardInterrupt:
        print("\nStopped")

with open("logs/vosk_log.txt", "w") as f:
    f.write(" ".join(vosk_transcript))