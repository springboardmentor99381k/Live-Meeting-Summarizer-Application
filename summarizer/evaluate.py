from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


def evaluate_summary(reference, generated):

    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rouge2', 'rougeL'],
        use_stemmer=True
    )

    rouge_scores = scorer.score(reference, generated)

    smoothie = SmoothingFunction().method1

    bleu_score = sentence_bleu(
        [reference.split()],
        generated.split(),
        smoothing_function=smoothie
    )

    results = {
        "ROUGE-1": rouge_scores['rouge1'].fmeasure,
        "ROUGE-2": rouge_scores['rouge2'].fmeasure,
        "ROUGE-L": rouge_scores['rougeL'].fmeasure,
        "BLEU": bleu_score
    }

    return results