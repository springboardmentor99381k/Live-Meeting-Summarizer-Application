import sounddevice as sd
from scipy.io.wavfile import write
import whisper

# Audio settings
fs = 16000        # Whisper works best at 16kHz
duration = 10     # seconds

print(" Recording started... Speak clearly")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
print(" Recording finished")

# Save audio
write("live_audio.wav", fs, audio)

print(" Loading Whisper model...")
model = whisper.load_model("base")

print(" Transcribing audio...")
result = model.transcribe("live_audio.wav")

print("\n Live Transcription:")
print(result["text"])
