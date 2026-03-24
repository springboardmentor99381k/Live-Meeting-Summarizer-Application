import sounddevice as sd
from scipy.io.wavfile import write

# Sampling frequency
fs = 44100  

# Duration of recording (seconds)
duration = 10  

print("🎙️ Recording will start now. Speak clearly...")
audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)

# Wait until recording is finished
sd.wait()

print("✅ Recording finished")

# Save as WAV file
write("test_audio.wav", fs, audio)

print("💾 Audio saved as test_audio.wav")
