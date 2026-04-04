import sounddevice as sd
import numpy as np
import wave
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_audio(duration=5, fs=16000, output_dir="temp", filename=None):
    """
    Record audio for a given duration and save to WAV file.

    - Sample rate: 16000 Hz
    - Mono channel
    - dtype int16
    - Normalizes amplitude
    """
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        filename = os.path.join(output_dir, f"chunk_{int(time.time())}.wav")

    logger.info("Recording started: %s seconds", duration)

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    # amplitude check
    max_amp = float(np.max(np.abs(recording)))
    if max_amp < 500:
        logger.warning("Low amplitude detected (%.2f). Audio may be too quiet.", max_amp)

    # normalize amplitude to prevent too-quiet chunks
    if max_amp > 0:
        normalized = (recording.astype(np.float32) / max_amp) * 32767
        normalized = np.clip(normalized, -32768, 32767).astype(np.int16)
    else:
        normalized = recording

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(normalized.tobytes())

    logger.info("Recording finished")
    logger.info("Saved chunk: %s", filename)

    return filename