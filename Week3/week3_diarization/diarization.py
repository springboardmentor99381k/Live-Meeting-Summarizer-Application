from pyannote.audio import Pipeline
import os

def run_diarization(audio_path):
    print("Loading diarization model...")

    HF_TOKEN = os.getenv("HF_TOKEN")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization@2.1",
        use_auth_token=HF_TOKEN
    )

    print("Running diarization...")
    diarization = pipeline(audio_path, num_speakers=2)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return segments