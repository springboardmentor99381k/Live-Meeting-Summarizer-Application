import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(filename, duration=15, fs=16000):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print("Saved:", filename)

if __name__ == "__main__":
    record_audio("Data/record.wav")