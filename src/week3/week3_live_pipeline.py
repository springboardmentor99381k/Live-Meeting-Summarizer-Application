import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
import os

# ==============================
# SETTINGS
# ==============================
SAMPLE_RATE = 16000
RECORD_SECONDS = 15
AUDIO_PATH = "Data/raw/live.wav"

# Ensure raw folder exists
os.makedirs("Data/raw", exist_ok=True)

# ==============================
# TEXT NORMALIZATION (Important for WER accuracy)
# ==============================
transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

# ==============================
# RECORD LIVE AUDIO
# ==============================
print("\nSpeak clearly... Recording for 15 seconds...\n")

audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE),
               samplerate=SAMPLE_RATE,
               channels=1)
sd.wait()

write(AUDIO_PATH, SAMPLE_RATE, audio)
print("Recording finished.\n")

# ==============================
# LOAD BETTER WHISPER MODEL
# ==============================
print("Loading Whisper model (small)...")
model = whisper.load_model("small")

print("Transcribing...\n")

result = model.transcribe(
    AUDIO_PATH,
    language="en",
    fp16=False
)

transcript = result["text"].strip()

print("===== LIVE TRANSCRIPT =====\n")
print(transcript)

# ==============================
# USER REFERENCE INPUT
# ==============================
print("\nType EXACTLY what you spoke (for accuracy calculation):")
reference = input("\nYour sentence: ")

# ==============================
# CLEAN BOTH TEXTS
# ==============================
reference_clean = transform(reference)
transcript_clean = transform(transcript)

# ==============================
# CALCULATE WER
# ==============================
error = wer(reference_clean, transcript_clean)
accuracy = (1 - error) * 100

print("\n===== EVALUATION =====")
print(f"Word Error Rate: {round(error * 100, 2)} %")
print(f"Accuracy: {round(accuracy, 2)} %")

if error < 0.15:
    print("Status: PASS (WER < 15%)")
else:
    print("Status: Needs Improvement")
    