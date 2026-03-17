from pyannote.audio import Pipeline

def run_diarization(audio_path):

    print("Loading diarization model...")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization"
    )

    print("Running diarization...")

    diarization = pipeline(audio_path, num_speakers=2)

    return diarization