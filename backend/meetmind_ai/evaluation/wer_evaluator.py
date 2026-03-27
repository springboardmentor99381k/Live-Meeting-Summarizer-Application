from jiwer import process_words, wer


class WEREvaluator:
    """Speech-to-text quality measurement using Word Error Rate (WER)."""

    def compute(self, reference_text: str, hypothesis_text: str) -> dict:
        """Compute WER and detailed error counts."""
        reference = (reference_text or "").strip()
        hypothesis = (hypothesis_text or "").strip()

        if not reference:
            return {
                "wer": 0.0,
                "substitutions": 0,
                "insertions": len(hypothesis.split()),
                "deletions": 0,
                "total_words": 0,
            }

        score = float(wer(reference, hypothesis))
        details = process_words(reference, hypothesis)

        return {
            "wer": score,
            "substitutions": int(details.substitutions),
            "insertions": int(details.insertions),
            "deletions": int(details.deletions),
            "total_words": int(details.hits + details.substitutions + details.deletions),
        }

    def interpret(self, wer_score: float) -> str:
        """Interpret WER score quality bands."""
        score = float(wer_score)

        if score < 0.10:
            return "Excellent"
        if score < 0.15:
            return "Good"
        if score < 0.25:
            return "Fair"
        return "Poor"
