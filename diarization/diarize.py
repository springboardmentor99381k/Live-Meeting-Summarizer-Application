

from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
)


def diarize_audio(audio_path):
    diarization = pipeline(audio_path)

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"{speaker}: {turn.start:.2f} - {turn.end:.2f}")