# evaluation_llm.py

from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import nltk

nltk.download("punkt")


def evaluate_summary(reference_text: str, generated_text: str):

    # ROUGE
    scorer = rouge_scorer.RougeScorer(
        ["rouge1", "rouge2", "rougeL"],
        use_stemmer=True
    )

    rouge_scores = scorer.score(reference_text, generated_text)

    # BLEU
    bleu_score = sentence_bleu(
        [reference_text.split()],
        generated_text.split()
    )

    return {
        "ROUGE-1": round(rouge_scores["rouge1"].fmeasure, 4),
        "ROUGE-2": round(rouge_scores["rouge2"].fmeasure, 4),
        "ROUGE-L": round(rouge_scores["rougeL"].fmeasure, 4),
        "BLEU": round(bleu_score, 4)
    }
