from pyannote.audio import Pipeline
import torch
import soundfile as sf
import numpy as np


class SpeakerDiarization:
    def __init__(self, token):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=token
        )

    def diarize(self, audio_file):
        waveform, sample_rate = sf.read(audio_file)

        if len(waveform.shape) == 2:
            waveform = np.mean(waveform, axis=1)

        waveform = torch.tensor(waveform, dtype=torch.float32).unsqueeze(0)

        return self.pipeline({
            "waveform": waveform,
            "sample_rate": sample_rate
        })