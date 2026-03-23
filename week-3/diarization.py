# diarization.py

from pyannote.audio import Pipeline
import torch
import soundfile as sf
import numpy as np

import warnings
warnings.filterwarnings("ignore", message=".*torchcodec is not installed correctly.*")
warnings.filterwarnings("ignore", message=".*degrees of freedom is <= 0.*")

def load_diarization_pipeline(hf_token: str):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=hf_token
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)
    return pipeline


def diarize_audio(wav_path: str, pipeline, num_speakers=None) -> list:
    """Load audio manually to bypass torchaudio/torchcodec issue"""
    
    # Load audio using soundfile instead of torchaudio
    waveform_np, sample_rate = sf.read(wav_path, dtype='float32', always_2d=True)
    # soundfile returns (samples, channels) → convert to (channels, samples)
    waveform_np = waveform_np.T
    waveform_tensor = torch.from_numpy(waveform_np)

    # Pass as dict to bypass torchaudio loading inside pyannote
    audio_dict = {
        "waveform": waveform_tensor,
        "sample_rate": sample_rate
    }

    if num_speakers:
        diarization = pipeline(audio_dict, num_speakers=num_speakers)
    else:
        diarization = pipeline(audio_dict)

    # NEW - replace with this:
    segments = []

    # Extract speakers from whatever output format pyannote dumps out
    # Modern pyannote pipelines return DiarizeOutput which wraps an Annotation
    # Sometimes it's the annotation directly. Check for `.itertracks` recursively
    target_obj = None

    if hasattr(diarization, 'itertracks'):
        target_obj = diarization
    elif hasattr(diarization, 'exclusive_speaker_diarization'):
        target_obj = diarization.exclusive_speaker_diarization
    elif hasattr(diarization, 'speaker_diarization'):
        target_obj = diarization.speaker_diarization
    elif hasattr(diarization, '_timeline'):
        target_obj = diarization
    elif hasattr(diarization, 'diarization'):
        target_obj = diarization.diarization
        
    if target_obj is None:
        raise ValueError(f"Unknown PyAnnote output structure. Dir: {dir(diarization)}")
        
    for turn, _, speaker in target_obj.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })

    return segments