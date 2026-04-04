from jiwer import wer
from stt.vosk_transcriber import transcribe_audio

reference = open("data/reference.txt").read()

prediction = transcribe_audio("data/meeting.wav")

error = wer(reference, prediction)

print("Prediction:", prediction)
print("WER:", error)