import threading
import wave
from queue import Queue
from typing import Optional

try:
    import pyaudio
except Exception:  # pragma: no cover - runtime/platform dependent import
    pyaudio = None

from meetmind_ai.config.settings import AUDIO_CHANNELS, AUDIO_CHUNK_SIZE, AUDIO_SAMPLE_RATE


class AudioCapture:
    """Real-time microphone capture using PyAudio."""

    def __init__(self, audio_queue: Queue):
        """
        Args:
            audio_queue: Thread-safe queue.Queue used to publish raw audio chunks.
        """
        self.audio_queue = audio_queue
        self.frames = []

        self._audio_interface: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._stop_event = threading.Event()
        self._recording_thread: Optional[threading.Thread] = None
        self._frames_lock = threading.Lock()
        self._is_available = pyaudio is not None

        if not self._is_available:
            print("[AudioCapture] PyAudio is not installed. Live recording is unavailable on this environment.")

    def start_recording(self) -> None:
        """Open the microphone stream and start a daemon reader thread."""
        if not self._is_available:
            print("[AudioCapture] Cannot start recording: PyAudio is unavailable.")
            return

        if self._recording_thread and self._recording_thread.is_alive():
            print("[AudioCapture] Recording is already running.")
            return

        self._stop_event.clear()

        try:
            self._audio_interface = pyaudio.PyAudio()
            self._stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_SAMPLE_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK_SIZE,
            )
        except Exception as exc:
            print(f"[AudioCapture] Failed to open audio stream: {exc}")
            self._cleanup_stream()
            return

        def _record_loop() -> None:
            while not self._stop_event.is_set():
                try:
                    chunk = self._stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                    self.audio_queue.put(chunk)
                    with self._frames_lock:
                        self.frames.append(chunk)
                except Exception as exc:
                    print(f"[AudioCapture] Stream read error: {exc}")
                    break

            self._cleanup_stream()

        self._recording_thread = threading.Thread(target=_record_loop, daemon=True, name="Thread 1")
        self._recording_thread.start()

    def stop_recording(self) -> None:
        """Signal recording thread to stop and close stream resources."""
        self._stop_event.set()

        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=2.0)

        self._cleanup_stream()

    def save_wav(self, filepath: str) -> None:
        """Save all captured frames to a WAV file."""
        try:
            sample_width = 2
            if self._audio_interface is not None and pyaudio is not None:
                sample_width = self._audio_interface.get_sample_size(pyaudio.paInt16)

            with self._frames_lock:
                frames_data = b"".join(self.frames)

            with wave.open(filepath, "wb") as wav_file:
                wav_file.setnchannels(AUDIO_CHANNELS)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(AUDIO_SAMPLE_RATE)
                wav_file.writeframes(frames_data)
        except Exception as exc:
            print(f"[AudioCapture] Failed to save WAV to '{filepath}': {exc}")

    def _cleanup_stream(self) -> None:
        """Close stream and terminate PyAudio safely."""
        if self._stream is not None:
            try:
                if self._stream.is_active():
                    self._stream.stop_stream()
            except Exception as exc:
                print(f"[AudioCapture] Error stopping stream: {exc}")
            try:
                self._stream.close()
            except Exception as exc:
                print(f"[AudioCapture] Error closing stream: {exc}")
            finally:
                self._stream = None

        if self._audio_interface is not None:
            try:
                self._audio_interface.terminate()
            except Exception as exc:
                print(f"[AudioCapture] Error terminating PyAudio: {exc}")
            finally:
                self._audio_interface = None
