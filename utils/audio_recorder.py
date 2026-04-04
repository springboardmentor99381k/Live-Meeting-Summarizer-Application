import sounddevice as sd
import soundfile as sf
import numpy as np

def record_audio(filename="data/meeting.wav", duration=10):

    samplerate = 16000

    print("Recording... Speak now")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16"   # IMPORTANT for Vosk
    )

    sd.wait()

    sf.write(filename, audio, samplerate, subtype="PCM_16")

    print("Audio saved:", filename)