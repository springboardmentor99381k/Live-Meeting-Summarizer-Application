import os
import re
import json
import wave

# Force ffmpeg for Whisper (Windows fix)
os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg\bin\ffmpeg.exe"

import whisper
from vosk import Model, KaldiRecognizer
from jiwer import wer


# =====================
# PATHS
# =====================

AUDIO = "audio/meeting1.wav"
REFERENCE = "transcripts/reference.txt"

WHISPER_OUT = "transcripts/whisper.txt"
VOSK_OUT = "transcripts/vosk.txt"

VOSK_MODEL_PATH = r"D:\speech_project\vosk-model-en-us-0.22"   # better than small model


# =====================
# TEXT CLEANING
# =====================

def clean(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================
# WHISPER
# =====================

print("\n🎙 Running Whisper...")

whisper_model = whisper.load_model("medium")  # better accuracy than base

whisper_result = whisper_model.transcribe(
    AUDIO,
    fp16=False,
    language="en"
)

whisper_text = whisper_result["text"]

with open(WHISPER_OUT, "w", encoding="utf-8") as f:
    f.write(whisper_text)


# =====================
# VOSK
# =====================

print("🎧 Running Vosk...")

vosk_model = Model(VOSK_MODEL_PATH)

wf = wave.open(AUDIO, "rb")
rec = KaldiRecognizer(vosk_model, wf.getframerate())

vosk_text = ""

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        vosk_text += json.loads(rec.Result())["text"] + " "

vosk_text += json.loads(rec.FinalResult())["text"]

with open(VOSK_OUT, "w", encoding="utf-8") as f:
    f.write(vosk_text)


# =====================
# WER
# =====================

ref = open(REFERENCE, encoding="utf-8").read()

ref_c = clean(ref)
whisper_c = clean(whisper_text)
vosk_c = clean(vosk_text)

wer_whisper = wer(ref_c, whisper_c) * 100
wer_vosk = wer(ref_c, vosk_c) * 100


# =====================
# RESULTS
# =====================

print("\n====================")
print("📊 ACCURACY REPORT")
print("====================")

print(f"Whisper WER : {wer_whisper:.2f} %")
print(f"Vosk WER    : {wer_vosk:.2f} %")

print("\n📁 Transcripts saved in /transcripts/")
print("====================")