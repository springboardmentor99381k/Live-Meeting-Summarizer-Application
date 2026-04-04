from utils.audio_recorder import record_audio
from stt.vosk_transcriber import transcribe_audio
from diarization.diarize import diarize_audio
from summarization.summarizer import summarize_text
from jiwer import wer

audio_file = "data/meeting.wav"

print("STEP 1: Recording audio...")
record_audio(audio_file, duration=10)

print("STEP 2: Running Speech-to-Text...")
transcript = transcribe_audio(audio_file)

print("Transcript:")
print(transcript)

# ---------------- WER SECTION ----------------
try:
    reference = open("data/reference.txt").read()
    error = wer(reference, transcript)

    print("Prediction:", transcript)
    print("WER:", error)
except FileNotFoundError:
    print("reference.txt not found, skipping WER calculation")
# ---------------------------------------------

print("STEP 3: Running Diarization...")
segments = diarize_audio(audio_file)

print("Segments:")
print(segments)

print("STEP 4: Generating Summary...")
summary = summarize_text(transcript)

print("Summary:")
print(summary)