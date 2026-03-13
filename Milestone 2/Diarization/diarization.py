import numpy as np
np.NaN = np.nan

import whisper
from pyannote.audio import Pipeline

# 🔐 Replace with your HuggingFace token
HF_TOKEN = "hf_xxxxxxxxxxxxx"

MEETING_ID = "ES2002a"
AUDIO_FILE = r"Data\sample_5min.wav"   # change if needed
SYSTEM_RTTM = "system_output.rttm"

print("Loading models...")

# Load diarization model
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HF_TOKEN
)

whisper_model = whisper.load_model("tiny")

print("Running diarization...")
diarization = diarization_pipeline(AUDIO_FILE)

print("Running transcription...")
transcription = whisper_model.transcribe(AUDIO_FILE)

print("\n----- Final Output -----\n")

# 🔹 OPEN RTTM FILE FOR WRITING
with open(SYSTEM_RTTM, "w") as rttm_file:

    for segment in transcription["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        speaker_label = "Unknown"

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.start <= start <= turn.end:
                speaker_label = speaker
                break

        # Print nicely
        print(f"[{round(start,2)} - {round(end,2)}] {speaker_label}:")
        print(text.strip())
        print()

        # 🔹 SAVE PROPER RTTM FORMAT
        duration = end - start
        rttm_file.write(
            f"SPEAKER {MEETING_ID} 1 {start:.3f} {duration:.3f} <NA> <NA> {speaker_label} <NA> <NA>\n"
        )

print("system_output.rttm created successfully!")