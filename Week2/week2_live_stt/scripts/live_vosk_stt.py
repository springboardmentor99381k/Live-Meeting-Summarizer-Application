import sounddevice as sd
import queue
import json
import vosk
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
MODEL_PATH = os.path.join(BASE_DIR, "week1_stt_evaluation", "models", "vosk-model-small-en-us-0.15")

# MODEL_PATH = "../../week1_stt_evaluation/models/vosk-model-small-en-us-0.15"
SAMPLERATE = 16000
BLOCKSIZE = 4000

print("Loading Vosk model...")
model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, SAMPLERATE)
rec.SetWords(True)

print("Model loaded successfully.")
print("Start speaking... (Press Ctrl+C to stop)\n")



q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


try:
    with sd.RawInputStream(
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        print("Microphone is active...\n")

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text")

                if text.strip() != "":
                    print("\nYou said:", text)
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial")

                if partial_text.strip() != "":
                    print("Partial:", partial_text, end="\r")


except KeyboardInterrupt:
    print("\n\nStopping microphone...")
    print("Program exited successfully.")

except Exception as e:
    print("\nError:", str(e))
