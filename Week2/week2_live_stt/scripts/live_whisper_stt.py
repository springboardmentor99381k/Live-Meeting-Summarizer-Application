import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os

SAMPLE_RATE = 16000
CHUNK_DURATION = 2

print("Loading Whisper model...")
model = whisper.load_model("base")

print("🎤 Start speaking... Press Ctrl+C to stop.")

try:
    while True:
        print("\nRecording...")
        audio = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE),
                       samplerate=SAMPLE_RATE,
                       channels=1,
                       dtype='int16')
        sd.wait()

        print("Audio max value:", np.max(audio))

        # Normalize
        audio_float = audio.astype(np.float32) / 32768.0

        temp_path = tempfile.mktemp(suffix=".wav")
        wav.write(temp_path, SAMPLE_RATE, audio_float)

        print("Transcribing...")
        result = model.transcribe(temp_path, language="en", fp16=False)

        text = result["text"].strip()
        print("RAW RESULT:", result)

        if text:
            print("You said:", text)

        os.remove(temp_path)

except KeyboardInterrupt:
    print("\nStopped Whisper live transcription.")