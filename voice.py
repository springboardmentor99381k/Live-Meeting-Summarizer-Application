import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import json
import time
import os
import csv
from vosk import Model, KaldiRecognizer
from jiwer import wer

# ---------------- SETTINGS ----------------
SAMPLE_RATE = 16000
DURATION = 10
NUM_SAMPLES = 3                     # Number of recordings
VOSK_MODEL_PATH = "model"           # Folder of Vosk model
RESULT_FILE = "results.csv"

# ---------------- LOAD MODELS ----------------
print("Loading Models...")

vosk_model = Model(VOSK_MODEL_PATH)
whisper_model = whisper.load_model("base")

print("Models Loaded Successfully!\n")

# ---------------- RECORD FUNCTION ----------------
def record_audio(filename):
    print(f"\n  Recording {filename} for {DURATION} seconds...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE),
                       samplerate=SAMPLE_RATE,
                       channels=1,
                       dtype='int16')
    sd.wait()
    wav.write(filename, SAMPLE_RATE, recording)
    print(" Recording saved.")


# ---------------- VOSK FUNCTION ----------------
def transcribe_vosk(audio_file):
    rec = KaldiRecognizer(vosk_model, SAMPLE_RATE)
    text = ""

    with open(audio_file, "rb") as wf:
        wf.read(44)
        while True:
            data = wf.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get("text", "") + " "

        final_result = json.loads(rec.FinalResult())
        text += final_result.get("text", "")

    return text.strip()


# ---------------- WHISPER FUNCTION ----------------
def transcribe_whisper(audio_file):
    result = whisper_model.transcribe(audio_file)
    return result["text"].strip()


# ---------------- MAIN PROCESS ----------------
results = []

for i in range(1, NUM_SAMPLES + 1):

    audio_file = f"audio_{i}.wav"
    ground_file = f"ground_{i}.txt"

    # Record audio
    record_audio(audio_file)

    # Check ground truth
    if not os.path.exists(ground_file):
        print(f"⚠ {ground_file} not found. Skipping accuracy calculation.")
        continue

    with open(ground_file, "r") as g:
        ground = g.read().lower()

    # -------- VOSK --------
    print("\n Running Vosk...")
    start = time.time()
    vosk_text = transcribe_vosk(audio_file).lower()
    vosk_time = time.time() - start
    vosk_wer = wer(ground, vosk_text)

    # -------- WHISPER --------
    print(" Running Whisper...")
    start = time.time()
    whisper_text = transcribe_whisper(audio_file).lower()
    whisper_time = time.time() - start
    whisper_wer = wer(ground, whisper_text)

    # Store results
    results.append([
        i,
        round(vosk_wer, 3),
        round((1 - vosk_wer) * 100, 2),
        round(vosk_time, 2),
        round(whisper_wer, 3),
        round((1 - whisper_wer) * 100, 2),
        round(whisper_time, 2)
    ])

    print("\n Sample", i, "Results:")
    print("Vosk -> WER:", round(vosk_wer, 3),
          "| Accuracy:", round((1 - vosk_wer) * 100, 2), "%",
          "| Time:", round(vosk_time, 2), "sec")

    print("Whisper -> WER:", round(whisper_wer, 3),
          "| Accuracy:", round((1 - whisper_wer) * 100, 2), "%",
          "| Time:", round(whisper_time, 2), "sec")

# ---------------- SAVE RESULTS ----------------
with open(RESULT_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Sample",
        "Vosk WER", "Vosk Accuracy (%)", "Vosk Time (s)",
        "Whisper WER", "Whisper Accuracy (%)", "Whisper Time (s)"
    ])
    writer.writerows(results)

print("\n Results saved to", RESULT_FILE)

# ---------------- FINAL AVERAGE ----------------
if results:
    avg_vosk_wer = sum(r[1] for r in results) / len(results)
    avg_whisper_wer = sum(r[4] for r in results) / len(results)

    print("\n ----- FINAL AVERAGE RESULT -----")
    print("Average Vosk WER:", round(avg_vosk_wer, 3))
    print("Average Whisper WER:", round(avg_whisper_wer, 3))

    if avg_vosk_wer < avg_whisper_wer:
        print("\n VOSK PERFORMS BETTER (Lower WER)")
    else:
        print("\n WHISPER PERFORMS BETTER (Lower WER)")
else:
    print("\nNo valid samples processed.")