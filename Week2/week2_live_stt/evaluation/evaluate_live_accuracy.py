from jiwer import wer

with open("reference.txt", "r", encoding="utf-8") as f:
    ref = f.read()

with open("whisper_output.txt", "r", encoding="utf-8") as f:
    hyp = f.read()

error = wer(ref, hyp)

print("WER:", error)
print("Accuracy:", (1 - error) * 100, "%")