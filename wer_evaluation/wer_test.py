from jiwer import wer

# Ground truth (what you actually spoke)
actual_text = "hello everyone this is a test of speech recognition system"

# Model prediction (copy from Whisper output)
predicted_text = "hello everyone this is test speech recognition system"

# Calculate WER
error = wer(actual_text, predicted_text)

print("Actual Text:")
print(actual_text)

print("\nPredicted Text:")
print(predicted_text)

print("\nWord Error Rate:", round(error, 3))
print("Accuracy:", round((1 - error) * 100, 2), "%")
