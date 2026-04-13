import sounddevice as sd
import numpy as np
import whisper
import torch
import queue
import threading
import time
from jiwer import wer

# ---------------- SETTINGS ----------------
SAMPLE_RATE = 16000
BUFFER_SECONDS = 5
MODEL_SIZE = "tiny"   # tiny = faster, base = more accurate

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading Whisper model...")
model = whisper.load_model(MODEL_SIZE).to(DEVICE)
print("Model loaded successfully!\n")

audio_queue = queue.Queue()
audio_buffer = np.zeros((0,), dtype=np.float32)

previous_text = ""
full_transcript = ""
running = True

# ---------------- AUDIO CALLBACK ----------------
def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# ---------------- TRANSCRIPTION THREAD ----------------
def transcribe():
    global audio_buffer, previous_text, full_transcript, running

    print("Start speaking... (Press Ctrl+C to stop)\n")

    while running:

        while not audio_queue.empty():
            data = audio_queue.get()
            data = np.squeeze(data)
            audio_buffer = np.concatenate((audio_buffer, data))

        if len(audio_buffer) >= SAMPLE_RATE * BUFFER_SECONDS:

            audio_chunk = audio_buffer[:SAMPLE_RATE * BUFFER_SECONDS]
            audio_buffer = audio_buffer[SAMPLE_RATE * 3:]  # sliding window

            result = model.transcribe(
                audio_chunk,
                fp16=False,
                temperature=0.0
            )

            text = result["text"].strip().lower()

            if text:

                # Remove repeated prefix
                if text.startswith(previous_text):
                    new_text = text[len(previous_text):].strip()
                else:
                    new_text = text

                if new_text:
                    print(new_text)
                    full_transcript += " " + new_text
                    previous_text = text

        time.sleep(0.2)

# ---------------- START STREAM ----------------
try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=1024,
        callback=callback
    ):
        thread = threading.Thread(target=transcribe)
        thread.start()

        while True:
            time.sleep(1)

except KeyboardInterrupt:
    running = False
    print("\nStopped.")

# ---------------- ACCURACY PART ----------------
print("\nAccuracy Evaluation")

reference = input("Enter the correct reference sentence:\n").lower().strip()
prediction = full_transcript.strip()

if reference and prediction:
    error = wer(reference, prediction)
    accuracy = max(0, (1 - error) * 100)

    print("\n----- FINAL RESULT -----")
    print("Predicted Text:", prediction)
    print("WER:", round(error, 3))
    print("Accuracy:", round(accuracy, 2), "%")
else:
    print("Reference or prediction missing.")
