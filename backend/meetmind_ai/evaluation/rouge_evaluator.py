from rouge_score import rouge_scorer


class ROUGEEvaluator:
    """Summarization quality measurement using ROUGE metrics."""

    def compute(self, reference_summary: str, generated_summary: str) -> dict:
        """Compute ROUGE-1/2/L F1 scores rounded to 4 decimal places."""
        reference = (reference_summary or "").strip()
        generated = (generated_summary or "").strip()

        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        scores = scorer.score(reference, generated)

        return {
            "rouge1": round(float(scores["rouge1"].fmeasure), 4),
            "rouge2": round(float(scores["rouge2"].fmeasure), 4),
            "rougeL": round(float(scores["rougeL"].fmeasure), 4),
        }

    def interpret(self, rouge1_score: float) -> str:
        """Interpret ROUGE-1 score quality bands."""
        score = float(rouge1_score)

        if score > 0.6:
            return "Excellent"
        if score > 0.4:
            return "Good"
        if score > 0.25:
            return "Fair"
        return "Poor"
