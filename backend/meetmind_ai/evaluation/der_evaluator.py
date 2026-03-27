from typing import Any, Dict, List

from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate


class DEREvaluator:
    """Diarization quality measurement using Diarization Error Rate (DER)."""

    def compute(
        self,
        reference_segments: List[Dict[str, Any]],
        hypothesis_segments: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Compute DER and component errors.

        Args:
            reference_segments: List of dicts with keys: speaker, start, end.
            hypothesis_segments: List of dicts with keys: speaker, start, end.

        Returns:
            Dict with der, missed_speech, false_alarm, speaker_confusion.
        """
        reference = self._to_annotation(reference_segments)
        hypothesis = self._to_annotation(hypothesis_segments)

        metric = DiarizationErrorRate()

        # Compute component totals first, then derive normalized rates.
        components = metric.compute_components(reference, hypothesis)

        total = float(components.get("total", 0.0))
        missed = float(components.get("missed detection", 0.0))
        false_alarm = float(components.get("false alarm", 0.0))
        confusion = float(components.get("confusion", 0.0))

        if total > 0:
            missed_speech = missed / total
            false_alarm_rate = false_alarm / total
            speaker_confusion = confusion / total
        else:
            missed_speech = 0.0
            false_alarm_rate = 0.0
            speaker_confusion = 0.0

        der = float(metric.compute_metric(components)) if total > 0 else 0.0

        return {
            "der": der,
            "missed_speech": missed_speech,
            "false_alarm": false_alarm_rate,
            "speaker_confusion": speaker_confusion,
        }

    def interpret(self, der_score: float) -> str:
        """Interpret DER score quality bands."""
        score = float(der_score)

        if score < 0.10:
            return "Excellent"
        if score < 0.20:
            return "Good"
        if score < 0.30:
            return "Fair"
        return "Poor"

    def _to_annotation(self, segments: List[Dict[str, Any]]) -> Annotation:
        """Convert list-of-dicts segment format to pyannote Annotation."""
        annotation = Annotation()

        for index, item in enumerate(segments or []):
            try:
                speaker = str(item["speaker"])
                start = float(item["start"])
                end = float(item["end"])
            except (KeyError, TypeError, ValueError):
                continue

            if end < start:
                start, end = end, start

            if end == start:
                continue

            annotation[Segment(start, end), index] = speaker

        return annotation
