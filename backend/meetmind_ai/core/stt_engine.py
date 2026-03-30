import threading
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from faster_whisper import WhisperModel

from meetmind_ai.config.settings import (
    AUDIO_CHANNELS,
    AUDIO_SAMPLE_RATE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_MODEL_SIZE,
)


class STTEngine:
    """Real-time and file-based speech-to-text using faster-whisper."""

    def __init__(self, audio_queue: Queue, transcript_callback: Callable[[str], None]):
        """
        Args:
            audio_queue: Thread-safe queue.Queue containing raw PCM bytes.
            transcript_callback: Callback invoked with transcribed text.
        """
        self.audio_queue = audio_queue
        self.transcript_callback = transcript_callback

        self._stop_event = threading.Event()
        self._transcription_thread: Optional[threading.Thread] = None

        self._bytes_per_sample = 2  # int16 PCM
        self._target_chunk_seconds = 2
        self._target_chunk_bytes = (
            AUDIO_SAMPLE_RATE * AUDIO_CHANNELS * self._bytes_per_sample * self._target_chunk_seconds
        )

        self.model: Optional[WhisperModel] = None
        try:
            self.model = WhisperModel(
                WHISPER_MODEL_SIZE,
                device=WHISPER_DEVICE,
                compute_type=WHISPER_COMPUTE_TYPE,
            )
        except Exception as exc:
            print(f"[STTEngine] Failed to load WhisperModel: {exc}")

    def start_transcription(self) -> None:
        """Start daemon transcription loop in Thread 2."""
        if self._transcription_thread and self._transcription_thread.is_alive():
            print("[STTEngine] Transcription is already running.")
            return

        if self.model is None:
            print("[STTEngine] Cannot start transcription: model is not loaded.")
            return

        self._stop_event.clear()

        def _transcription_loop() -> None:
            buffer = bytearray()

            while not self._stop_event.is_set():
                try:
                    chunk = self.audio_queue.get(timeout=0.2)
                except Empty:
                    continue
                except Exception as exc:
                    print(f"[STTEngine] Queue read error: {exc}")
                    continue

                if not chunk:
                    continue

                if not isinstance(chunk, (bytes, bytearray)):
                    print("[STTEngine] Ignoring non-bytes audio chunk.")
                    continue

                buffer.extend(chunk)

                if len(buffer) < self._target_chunk_bytes:
                    continue

                audio_bytes = bytes(buffer)
                buffer.clear()

                text = self._transcribe_bytes(audio_bytes)
                if text:
                    try:
                        self.transcript_callback(text)
                    except Exception as exc:
                        print(f"[STTEngine] transcript_callback error: {exc}")

            # Flush any remaining audio when stopping.
            if buffer:
                text = self._transcribe_bytes(bytes(buffer))
                if text:
                    try:
                        self.transcript_callback(text)
                    except Exception as exc:
                        print(f"[STTEngine] transcript_callback error: {exc}")

        self._transcription_thread = threading.Thread(
            target=_transcription_loop,
            daemon=True,
            name="Thread 2",
        )
        self._transcription_thread.start()

    def stop_transcription(self) -> None:
        """Signal transcription loop to stop cleanly."""
        self._stop_event.set()

        if self._transcription_thread and self._transcription_thread.is_alive():
            self._transcription_thread.join(timeout=2.0)

    def transcribe_file(self, wav_filepath: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Transcribe an entire WAV file and return full text with timestamps."""
        if self.model is None:
            print("[STTEngine] Cannot transcribe file: model is not loaded.")
            return "", []

        try:
            segments, _info = self.model.transcribe(
                wav_filepath,
                beam_size=5,
                language="en",
            )

            texts: List[str] = []
            timestamps: List[Dict[str, Any]] = []

            for segment in segments:
                segment_text = segment.text.strip()
                if not segment_text:
                    continue

                texts.append(segment_text)
                timestamps.append(
                    {
                        "start": float(segment.start),
                        "end": float(segment.end),
                        "text": segment_text,
                    }
                )

            full_transcript = " ".join(texts).strip()
            return full_transcript, timestamps
        except Exception as exc:
            print(f"[STTEngine] File transcription error for '{wav_filepath}': {exc}")
            return "", []

    def _transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Run faster-whisper on raw PCM bytes and return joined segment text."""
        if self.model is None or not audio_bytes:
            return ""

        try:
            samples = np.frombuffer(audio_bytes, dtype=np.int16)
            if samples.size == 0:
                return ""

            if AUDIO_CHANNELS > 1:
                # Convert interleaved multi-channel audio to mono for Whisper.
                samples = samples.reshape(-1, AUDIO_CHANNELS).mean(axis=1).astype(np.int16)

            audio_float32 = samples.astype(np.float32) / 32768.0

            segments, _info = self.model.transcribe(
                audio_float32,
                beam_size=5,
                language="en",
            )

            texts: List[str] = []
            for segment in segments:
                segment_text = segment.text.strip()
                if segment_text:
                    texts.append(segment_text)

            return " ".join(texts).strip()
        except Exception as exc:
            print(f"[STTEngine] Real-time transcription error: {exc}")
            return ""
