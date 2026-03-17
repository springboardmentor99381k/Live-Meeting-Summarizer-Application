import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav


def record_audio(filename="recorded_meeting.wav", duration=10):
    print("Recording started... Speak now")

    # ✅ Get default mic
    device_info = sd.query_devices(kind='input')

    samplerate = int(device_info['default_samplerate'])  # ✅ AUTO FIX

    print(f"Using Device: {device_info['name']}")
    print(f"Sample Rate: {samplerate}")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    print("Recording finished")

    audio = np.squeeze(audio)

    wav.write(filename, samplerate, audio)

    print(f"Audio saved as {filename}")