from jiwer import wer

REFERENCE_PATH = "../transcripts/reference.txt"
VOSK_PATH = "../outputs/vosk_output.txt"
WHISPER_PATH = "../outputs/whisper_output.txt"

with open(REFERENCE_PATH, "r", encoding="utf-8") as f:
    reference = f.read()

with open(VOSK_PATH, "r", encoding="utf-8") as f:
    vosk_text = f.read()

with open(WHISPER_PATH, "r", encoding="utf-8") as f:
    whisper_text = f.read()

vosk_wer = wer(reference, vosk_text)
whisper_wer = wer(reference, whisper_text)

print("VOSK WER:", round(vosk_wer, 3))
print("WHISPER WER:", round(whisper_wer, 3))
