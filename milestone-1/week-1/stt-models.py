# milestone 1

pip install -q openai-whisper
pip install -q vosk
pip install -q jiwer
pip install -q soundfile
apt-get install -y ffmpeg
wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip -q vosk-model-small-en-us-0.15.zip

from google.colab import files
uploaded = files.upload()

import os
print(os.getcwd())
# whisper transcript model
import whisper

model = whisper.load_model("small")
result = model.transcribe("audio2.wav")

with open("whisper.txt", "w") as f:
    f.write(result["text"])

print("Whisper transcription complete.")
print(result["text"][:500])
# vosk transcript model
from vosk import Model, KaldiRecognizer
import wave
import json

wf = wave.open("audio2.wav", "rb")
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, wf.getframerate())

results = []

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        results.append(json.loads(rec.Result())["text"])

results.append(json.loads(rec.FinalResult())["text"])
final_text = " ".join(results)

with open("vosk.txt", "w") as f:
    f.write(final_text)

print("Vosk transcription complete.")
print(final_text[:500])

# Wav2Vec transcript model
pip install -q transformers torchaudio jiwer datasets accelerate

import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from google.colab import files

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "facebook/wav2vec2-base-960h"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device)
model.eval()

uploaded = files.upload()
file_path = list(uploaded.keys())[0]

speech, sr = torchaudio.load(file_path)
if speech.shape[0] > 1:
    speech = torch.mean(speech, dim=0, keepdim=True)
if sr != 16000:
    resampler = torchaudio.transforms.Resample(sr, 16000)
    speech = resampler(speech)
speech = speech.squeeze()

chunk_length = 20
sampling_rate = 16000
chunk_size = chunk_length * sampling_rate
speech = speech.to(device)
transcriptions = []

for i in range(0, speech.shape[0], chunk_size):
    chunk = speech[i:i + chunk_size]
    inputs = processor(chunk.cpu(), sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    input_values = inputs.input_values.to(device)
    with torch.no_grad():
        logits = model(input_values).logits
    pred_ids = torch.argmax(logits, dim=-1)
    transcriptions.append(processor.batch_decode(pred_ids)[0])
    torch.cuda.empty_cache()

final_transcription = " ".join(transcriptions)
print("\nFinal Transcription:\n")
print(final_transcription)

with open("wav2vec_transcription.txt", "w") as f:
    f.write(final_transcription)
print("\n Transcription saved as wav2vec_transcription.txt")

from jiwer import wer

# Load your Wav2Vec transcription
reference = open("reference_audio2.txt").read().lower()
wav2vec_pred = open("wav2vec_transcription.txt").read().lower()

wav2vec_wer = wer(reference, wav2vec_pred)

print("\n")
print(f"Wav2Vec WER: {wav2vec_wer*100:.2f}%")

from jiwer import wer

reference = open("reference_audio2.txt").read().lower()
whisper_pred = open("whisper.txt").read().lower()
vosk_pred = open("vosk.txt").read().lower()

whisper_wer = wer(reference, whisper_pred)
vosk_wer = wer(reference, vosk_pred)

print(f"Whisper WER: {whisper_wer * 100:.2f}%")
print(f"Vosk WER: {vosk_wer * 100:.2f}%")

report = f"""
Dataset: AMI Meeting Corpus (sample)

Whisper-small WER: {whisper_wer * 100:.2f}%
Vosk-small WER: {vosk_wer * 100:.2f}%
Wav2Vec2 WER: {wav2vec_wer * 100:.2f}%

Conclusion:
{"Whisper performs best." if whisper_wer <= vosk_wer and whisper_wer <= wav2vec_wer
 else "Vosk performs best." if vosk_wer <= whisper_wer and vosk_wer <= wav2vec_wer
 else "Wav2Vec2 performs best."}
"""

with open("WER_Report.txt", "w") as f:
    f.write(report)

print(report)

files.download("whisper.txt")
files.download("vosk.txt")
files.download("WER_Report.txt")