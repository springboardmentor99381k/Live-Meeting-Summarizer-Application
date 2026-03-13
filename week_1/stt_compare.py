import json
import wave
from vosk import Model, KaldiRecognizer
import whisper
from jiwer import wer
import soundfile as sf
import os
import numpy as np
from scipy.io import wavfile
import tempfile
import sys
import logging
from contextlib import contextmanager

# Suppress logging
logging.getLogger("whisper").setLevel(logging.ERROR)
logging.getLogger("vosk").setLevel(logging.ERROR)

@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output"""
    save_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = save_stderr

AUDIO_PATH = "audio/meeting.wav"
REFERENCE_PATH = "audio/meeting.txt"
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"

os.makedirs("results", exist_ok=True)

# Load reference transcript
with open(REFERENCE_PATH, "r", encoding="utf-8") as f:
    reference_text = f.read().strip().lower()

# VOSK TRANSCRIPTION
def transcribe_vosk(audio_path):
    wf = wave.open(audio_path, "rb")

    with suppress_stderr():
        model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "

    final_res = json.loads(rec.FinalResult())
    result_text += final_res.get("text", "")

    return result_text.strip().lower()

# WHISPER TRANSCRIPTION
def transcribe_whisper(audio_path):
    # Load audio using soundfile to avoid ffmpeg dependency
    audio_data, sr = sf.read(audio_path)
    
    # Ensure mono audio
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Convert to float32 for Whisper
    audio_data = audio_data.astype(np.float32)
    
    # Normalize audio to [-1, 1] range
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val
    
    # Resample to 16kHz if needed
    target_sr = 16000
    if sr != target_sr:
        num_samples = int(len(audio_data) * target_sr / sr)
        audio_data = np.interp(np.linspace(0, len(audio_data), num_samples), 
                               np.arange(len(audio_data)), audio_data)
        audio_data = audio_data.astype(np.float32)
    
    # Use Whisper's internal processing without ffmpeg
    model = whisper.load_model("base")
    result = model.transcribe(audio_data, language="en", fp16=False)
    return result["text"].strip().lower()

# Run Transcriptions
print("Running Vosk...")
vosk_text = transcribe_vosk(AUDIO_PATH)

print("Running Whisper...")
whisper_text = transcribe_whisper(AUDIO_PATH)

# Save outputs
with open("results/vosk_output.txt", "w", encoding="utf-8") as f:
    f.write(vosk_text)

with open("results/whisper_output.txt", "w", encoding="utf-8") as f:
    f.write(whisper_text)

# Calculate WER
vosk_wer = wer(reference_text, vosk_text)
whisper_wer = wer(reference_text, whisper_text)

# Save WER Report
with open("results/wer_report.txt", "w", encoding="utf-8") as f:
    f.write(f"Vosk WER: {vosk_wer:.2f}\n")
    f.write(f"Whisper WER: {whisper_wer:.2f}\n")

print("\n--- RESULTS ---")
print(f"Vosk WER: {vosk_wer:.2f}")
print(f"Whisper WER: {whisper_wer:.2f}")
