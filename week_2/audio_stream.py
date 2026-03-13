import sounddevice as sd
import queue
import sys

samplerate = 16000
block_size = 8000
audio_queue = queue.Queue()

sd.default.latency = "high"

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

def start_stream():
    return sd.RawInputStream(
        samplerate=samplerate,
        blocksize=block_size,
        dtype="int16",
        channels=1,
        callback=audio_callback
    )