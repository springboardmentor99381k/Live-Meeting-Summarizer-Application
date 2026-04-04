import os

from typing import Any, Dict, List, Optional

import torch
import torchaudio
from pyannote.audio import Pipeline


def run_diarization(audio_file: str) -> Optional[List[Dict[str, Any]]]:
    """Run speaker diarization and return speaker segments with timestamps.

    Uses a Hugging Face token stored in the HUGGINGFACE_TOKEN environment
    variable (never hard-coded).

    Returns a list of segments like:
        [{"start": 0.0, "end": 4.12, "speaker": "SPEAKER_00"}, ...]

    The latest pyannote API expects `token=` instead of `use_auth_token=`.

    This function avoids internal pyannote decoding by loading audio through
    torchaudio and passing waveform/sample_rate directly.
    """
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("Hugging Face token not found. Please set HUGGINGFACE_TOKEN environment variable.")
        return None

    try:
        print("Running speaker diarization...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=token,
        )

        # Ensure the model runs on CPU to avoid GPU requirements.
        pipeline.to(torch.device("cpu"))

        # Load audio using torchaudio to avoid pyannote's internal decoding.
        waveform, sample_rate = torchaudio.load(audio_file)

        diarization = pipeline({"waveform": waveform, "sample_rate": int(sample_rate)})

        # Convert pyannote's output into a simple list of timestamped speaker segments
        segments: List[Dict[str, Any]] = []
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            start = float(segment.start)
            end = float(segment.end)
            speaker_label = str(speaker)

            # Print speaker segments so the user can see diarization progress.
            print(f"  {speaker_label}: {start:.2f}s → {end:.2f}s")

            segments.append({
                "start": start,
                "end": end,
                "speaker": speaker_label,
            })

        print("Diarization completed")
        return segments
    except Exception as e:
        print(f"Diarization failed: {e}")
        return None
