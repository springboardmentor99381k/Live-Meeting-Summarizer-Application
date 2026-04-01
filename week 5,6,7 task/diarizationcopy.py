import numpy as np
np.NaN = np.nan

import re
from collections import defaultdict
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

# 🔐 Your Hugging Face Token
HF_TOKEN = "YOUR HUGGING FACE TOKEN"

# 🔊 Load models ONLY once (important)
diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HF_TOKEN
)

# ⚡ Faster Whisper Model
whisper_model = WhisperModel("tiny", compute_type="int8")


def run_diarization(file_path):

    diarization = diarization_pipeline(file_path)
    segments, _ = whisper_model.transcribe(file_path)

    # ✅ DEFINE HERE (before loop)
    speaker_map = {}
    speaker_count = 1
    output = []

    for segment in segments:
        start = round(segment.start, 2)
        end = round(segment.end, 2)
        text = segment.text.strip()

        if len(text.split()) < 2:
            continue

        text = re.sub(r"\s+", " ", text)

        speaker_label = None

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if (turn.start <= start <= turn.end) or (turn.start <= end <= turn.end):
                speaker_label = speaker
                break

        if speaker_label is None:
            speaker_label = "UNKNOWN"

        # ✅ NOW THIS WILL WORK
        if speaker_label not in speaker_map:
            speaker_map[speaker_label] = f"Speaker {speaker_count}"
            speaker_count += 1

        speaker_name = speaker_map[speaker_label]

        line = f"[{start} - {end}] {speaker_name}: {text}"

        if line not in output:
            output.append(line)

    return "\n\n".join(output)