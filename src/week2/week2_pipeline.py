import whisper
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip

AUDIO_PATH = "Data/raw/sample.wav"
REFERENCE_PATH = "transcripts/reference/sample.txt"

# -------- TEXT NORMALIZATION PIPELINE --------
transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

print("Loading Whisper model...")
model = whisper.load_model("base")

print("Transcribing audio...")
result = model.transcribe(AUDIO_PATH)
transcript = result["text"]

print("\n===== TRANSCRIPT =====\n")
print(transcript)

# Save transcript
with open("transcripts/whisper/sample.txt", "w", encoding="utf-8") as f:
    f.write(transcript)

# Load reference
with open(REFERENCE_PATH, "r", encoding="utf-8") as f:
    reference = f.read()

# Normalize both texts
reference_clean = transform(reference)
transcript_clean = transform(transcript)

# Calculate WER
error = wer(reference_clean, transcript_clean)
accuracy = (1 - error) * 100

print("\n===== EVALUATION =====")
print(f"Word Error Rate: {round(error * 100, 2)} %")
print(f"Accuracy: {round(accuracy, 2)} %")

if error < 0.15:
    print("Status: PASS (WER < 15%)")
else:
    print("Status: Needs Improvement")