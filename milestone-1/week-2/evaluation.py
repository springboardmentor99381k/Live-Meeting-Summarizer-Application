from jiwer import wer, cer

def evaluate(predictions, references):

    ref = " ".join(references)
    hyp = " ".join(predictions)

    print("\n------ Accuracy ------")
    print("WER:", wer(ref, hyp))
    print("CER:", cer(ref, hyp))