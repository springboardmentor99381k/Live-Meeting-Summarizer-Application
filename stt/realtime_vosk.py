import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

model = Model("models/vosk-model-small-en-us-0.15")

def stream_transcription(callback_text):

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    rec = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    callback_text(text)