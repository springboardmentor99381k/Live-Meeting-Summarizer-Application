import sounddevice as sd
import queue
import json
import time
from vosk import Model, KaldiRecognizer
from jiwer import wer

MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
RECORD_SECONDS = 30

q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def main():
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)

    final_text = []

    print(f"🎤 Recording for {RECORD_SECONDS} seconds...\n")

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        start_time = time.time()

        while time.time() - start_time < RECORD_SECONDS:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result.get("text"):
                    print("📝", result["text"])
                    final_text.append(result["text"])

    print("\n🛑 Recording finished")

    vosk_output = " ".join(final_text)

    print("\n--- FINAL VOSK TRANSCRIPT ---")
    print(vosk_output)

    reference = input("\n✍️ Type what you actually said:\n")

    error = wer(reference.lower(), vosk_output.lower())

    print(f"\n📊 WER: {error * 100:.2f}%")

    if error <= 0.15:
        print("✅ WER < 15% (GOOD)")
    else:
        print("❌ WER > 15% (Needs improvement)")

if __name__ == "__main__":
    main()