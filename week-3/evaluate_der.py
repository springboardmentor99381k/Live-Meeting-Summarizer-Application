# evaluate_der.py
# pip install pyannote.metrics

from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.core import Annotation, Segment
import json

def compute_der(hypothesis_segments: list, reference_rttm_path: str):
    """
    Compare your diarization output vs AMI ground truth RTTM.
    DER target: < 20%
    """
    metric = DiarizationErrorRate()

    # Build hypothesis annotation from your output
    hypothesis = Annotation()
    for seg in hypothesis_segments:
        hypothesis[Segment(seg["start"], seg["end"])] = seg["speaker"]

    # Load reference from AMI RTTM file
    reference = Annotation()
    with open(reference_rttm_path) as f:
        for line in f:
            parts = line.strip().split()
            if parts[0] == "SPEAKER":
                start = float(parts[3])
                duration = float(parts[4])
                speaker = parts[7]
                reference[Segment(start, start + duration)] = speaker

    der = metric(reference, hypothesis)
    print(f"Diarization Error Rate (DER): {der * 100:.2f}%")
    return der


if __name__ == "__main__":
    # Load hypothesis from diarized_output.json
    try:
        with open("diarized_output.json") as f:
            data = json.load(f)
            segments = data.get("diarization_segments", [])
    except FileNotFoundError:
        print("Please run main_diarization.py first to generate diarized_output.json")
        exit(1)

    # Compute DER
    print("Evaluating Diarization Error Rate (DER)...")
    compute_der(segments, "ami_sample.rttm")
