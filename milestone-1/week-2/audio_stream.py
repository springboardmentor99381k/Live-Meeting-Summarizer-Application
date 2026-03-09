import sounddevice as sd
import numpy as np
import queue

audio_queue = queue.Queue()

SAMPLERATE = 16000
CHUNK_SECONDS = 4

# NEW: Store full recording for saving
recorded_frames = []

def callback(indata, frames, time, status):
    if status:
        print(status)

    # For real-time STT chunks
    audio_queue.put(indata.copy())

    # For saving complete audio
    recorded_frames.append(indata.copy())


def start_stream():
    return sd.InputStream(
        samplerate=SAMPLERATE,
        channels=1,
        callback=callback
    )


def get_audio_chunk():
    frames = []
    samples_needed = SAMPLERATE * CHUNK_SECONDS

    while len(frames) * 1024 < samples_needed:
        frames.append(audio_queue.get())

    audio = np.concatenate(frames, axis=0)
    return audio.flatten()


# Optional helper to reset recording
def clear_recording():
    recorded_frames.clear()
