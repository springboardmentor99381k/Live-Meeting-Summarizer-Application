from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.core import Annotation, Segment

REFERENCE_RTTM = "Diarization/reference_5min.rttm"
SYSTEM_RTTM = "Diarization/system_output.rttm"


def load_rttm(file_path):
    annotation = Annotation()

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 8:
                continue

            start = float(parts[3])
            duration = float(parts[4])
            speaker = parts[7]

            segment = Segment(start, start + duration)
            annotation[segment] = speaker

    return annotation


print("Loading reference RTTM...")
reference = load_rttm(REFERENCE_RTTM)

print("Loading system RTTM...")
hypothesis = load_rttm(SYSTEM_RTTM)

print("Calculating DER...")

metric = DiarizationErrorRate()
der = metric(reference, hypothesis)

accuracy = (1 - der) * 100

print("\n==============================")
print(f"DER: {der * 100:.2f}%")
print(f"Accuracy: {accuracy:.2f}%")
print("==============================\n")