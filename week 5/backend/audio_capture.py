import sounddevice as sd
import numpy as np
import queue
import threading
import soundfile as sf
from pathlib import Path

_recording_thread = None
_stop_event = threading.Event()
_audio_queue = queue.Queue()

SAMPLE_RATE = 16000
CHANNELS = 1


def _recording_worker():
    """Background thread that captures audio frames into a queue."""

    def callback(indata, frames, time, status):
        if status:
            print(f"Audio stream status: {status}")
        _audio_queue.put(indata.copy())

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
            while not _stop_event.is_set():
                sd.sleep(100)
    except Exception as e:
        print(f"Audio capture error: {e}")


def start_recording():
    """Start audio recording in a background thread."""
    global _recording_thread

    if _recording_thread and _recording_thread.is_alive():
        print("Recording already in progress")
        return

    # Drain any old frames
    while not _audio_queue.empty():
        _audio_queue.get()

    _stop_event.clear()
    _recording_thread = threading.Thread(target=_recording_worker, daemon=True)
    _recording_thread.start()
    print("Recording started...")


def stop_recording(output_path: str = "meeting.wav"):
    """Stop recording and write captured audio to a WAV file."""
    global _recording_thread

    if not _recording_thread or not _recording_thread.is_alive():
        print("No recording in progress")
        return

    _stop_event.set()
    _recording_thread.join()

    audio_chunks = []
    while not _audio_queue.empty():
        audio_chunks.append(_audio_queue.get())

    if not audio_chunks:
        print("No audio recorded")
        return

    audio_data = np.concatenate(audio_chunks, axis=0)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), audio_data, SAMPLE_RATE)
    print(f"Recording saved as {output_path}")
