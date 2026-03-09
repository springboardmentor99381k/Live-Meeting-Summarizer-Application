from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.core import Annotation, Segment


def load_rttm(rttm_file):
    annotation = Annotation()

    with open(rttm_file, "r") as f:
        for line in f:
            if line.startswith("SPEAKER"):
                parts = line.strip().split()
                start = float(parts[3])
                duration = float(parts[4])
                speaker = parts[7]

                segment = Segment(start, start + duration)
                annotation[segment] = speaker

    return annotation


def compute_der(reference_rttm, system_rttm):
    ref = load_rttm(reference_rttm)
    hyp = load_rttm(system_rttm)

    metric = DiarizationErrorRate(collar=0.25, skip_overlap=False)
    der = metric(ref, hyp)

    print(f"DER: {der * 100:.2f}%")
    return der


if __name__ == "__main__":
    reference_file = "references/reference-IS1009a.rttm"
    predicted_file = "results/system.rttm"

    compute_der(reference_file, predicted_file)
