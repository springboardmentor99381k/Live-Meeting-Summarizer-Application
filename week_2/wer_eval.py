from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

# Vosk evaluation
with open("reference_vosk.txt",encoding="utf-8") as f:
    ref_vosk = transform(f.read())

with open("logs/vosk_log.txt", encoding="utf-8") as f:
    hyp_vosk = transform(f.read())

print(f"Vosk WER: {wer(ref_vosk, hyp_vosk):.2%}")

# Whisper evaluation
with open("reference_whisper.txt",encoding="utf-8") as f:
    ref_whisper = transform(f.read())

with open("logs/whisper_log.txt", encoding="utf-8") as f:
    hyp_whisper = transform(f.read())

print(f"Whisper WER: {wer(ref_whisper, hyp_whisper):.2%}")

