import os
from pyannote.audio import Pipeline

# Get token from environment variable
HF_TOKEN = os.getenv("HF_TOKEN")

print("Loading pipeline...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization@2.1",
    use_auth_token=HF_TOKEN
)

print("Running diarization...")
diarization = pipeline("Week3/week3_diarization/short.wav", num_speakers=2)

print("Finished processing!")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.2f}s --> {turn.end:.2f}s | {speaker}")