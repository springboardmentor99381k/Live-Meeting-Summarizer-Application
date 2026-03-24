import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from jiwer import wer
import re

# ==========================
# SETTINGS
# ==========================

fs = 16000        # Sample rate
duration = 8      # Recording duration (seconds)

# ==========================
# CLEAN TEXT FUNCTION
# ==========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ==========================
# RECORD AUDIO
# ==========================

print("🎙 Speak now... Recording for", duration, "seconds")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print("✅ Recording finished")

write("temp_audio.wav", fs, audio)

# ==========================
# LOAD WHISPER MODEL
# ==========================

print("\n🔄 Loading Whisper model...")
model = whisper.load_model("base")

print("🎧 Transcribing...")
result = model.transcribe("temp_audio.wav")

predicted_text = clean_text(result["text"])

print("\n📝 Predicted Transcription:")
print(predicted_text)

# ==========================
# GET GROUND TRUTH
# ==========================

actual_text = input("\n✏ Type EXACTLY what you spoke:\n")
actual_text = clean_text(actual_text)

# ==========================
# CALCULATE WER
# ==========================

error = wer(actual_text, predicted_text)
accuracy = (1 - error) * 100

print("\n========== RESULT ==========")
print("Word Error Rate:", round(error, 3))
print("Accuracy:", round(accuracy, 2), "%")
print("============================")

