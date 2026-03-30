import os
from typing import Dict, List, Optional

from meetmind_ai.config.settings import HUGGINGFACE_TOKEN


class Diarization:
    """Speaker diarization using pyannote.audio."""

    def __init__(self):
        self.pipeline = None
        self.last_error = ""

        if not HUGGINGFACE_TOKEN:
            self.last_error = "HUGGINGFACE_TOKEN is missing in settings."
            print(f"[Diarization] {self.last_error}")
            return

        try:
            from pyannote.audio import Pipeline

            model_id = "pyannote/speaker-diarization-3.1"
            try:
                # Newer huggingface_hub versions expect `token`.
                self.pipeline = Pipeline.from_pretrained(
                    model_id,
                    token=HUGGINGFACE_TOKEN,
                )
            except TypeError:
                # Backward compatibility for older stacks.
                self.pipeline = Pipeline.from_pretrained(
                    model_id,
                    use_auth_token=HUGGINGFACE_TOKEN,
                )

            if self.pipeline is None:
                self.last_error = (
                    "Could not load diarization pipeline. "
                    "Ensure HUGGINGFACE_TOKEN is valid and model terms are accepted at "
                    "https://hf.co/pyannote/speaker-diarization-3.1"
                )
                print(f"[Diarization] {self.last_error}")
        except Exception as exc:
            message = str(exc)
            if "NoneType" in message and "eval" in message:
                self.last_error = (
                    "Failed to load pyannote model dependencies. "
                    "Make sure your Hugging Face token has accepted terms for both "
                    "https://hf.co/pyannote/speaker-diarization-3.1 and "
                    "https://hf.co/pyannote/segmentation-3.0"
                )
            else:
                self.last_error = message
            if "401" in message or "403" in message or "token" in message.lower():
                print(
                    "[Diarization] Authentication error while loading pipeline. "
                    "Check HUGGINGFACE_TOKEN permissions and validity."
                )
            else:
                print(f"[Diarization] Failed to load diarization pipeline: {exc}")

    def run(self, wav_filepath: str) -> List[Dict[str, float]]:
        """Run diarization on a WAV file and return normalized segment dicts."""
        if not os.path.isfile(wav_filepath):
            self.last_error = f"WAV file not found: {wav_filepath}"
            print(f"[Diarization] {self.last_error}")
            return []

        if self.pipeline is None:
            if not self.last_error:
                self.last_error = "Pipeline is not available; cannot run diarization."
            print(f"[Diarization] {self.last_error}")
            return []

        try:
            raw_segments = self.pipeline(wav_filepath)
            segments = self.format_segments(raw_segments)

            if not segments:
                self.last_error = "No speaker segments detected."
                print(f"[Diarization] No speaker segments detected for file: {wav_filepath}")
                return []

            for segment in segments:
                print(
                    "[Diarization] "
                    f"speaker={segment['speaker']} "
                    f"start={segment['start']:.2f}s "
                    f"end={segment['end']:.2f}s"
                )

            return segments
        except Exception as exc:
            message = str(exc)
            if "401" in message or "403" in message or "token" in message.lower():
                self.last_error = (
                    "Authentication error while running diarization. "
                    "Verify HUGGINGFACE_TOKEN access to pyannote models."
                )
                print(
                    "[Diarization] Authentication error while running diarization. "
                    "Verify HUGGINGFACE_TOKEN access to pyannote models."
                )
            else:
                self.last_error = f"Diarization failed for '{wav_filepath}': {exc}"
                print(f"[Diarization] Diarization failed for '{wav_filepath}': {exc}")
            return []

    def is_available(self) -> bool:
        return self.pipeline is not None

    def format_segments(self, segments) -> List[Dict[str, float]]:
        """Convert pyannote diarization output into list-of-dicts format."""
        formatted: List[Dict[str, float]] = []

        if segments is None:
            return formatted

        try:
            for turn, _, speaker in segments.itertracks(yield_label=True):
                formatted.append(
                    {
                        "speaker": str(speaker),
                        "start": float(turn.start),
                        "end": float(turn.end),
                    }
                )
        except Exception as exc:
            print(f"[Diarization] Could not format diarization segments: {exc}")
            return []

        return formatted
