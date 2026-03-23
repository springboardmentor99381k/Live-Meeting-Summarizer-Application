from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import nltk

nltk.download('punkt')

# Reference summary (manual ground truth)
reference_summary = """
The meeting focused on developing a prototype system while avoiding duplication of effort. 
Participants discussed prioritizing the interface development using existing components. 
The team also reviewed compatibility with the Knight XML framework and emphasized understanding 
its documentation and structure. Discussions also covered online and offline data processing 
and how the interface mainly acts as a viewer of data loaded from files.
"""

# Generated summary (Groq output)
generated_summary = """
The meeting discussed the development of a prototype and its components with focus on data structure 
and compatibility with the Knight XML framework. The team emphasized minimizing duplication of effort, 
building a prototype using ready-made components, and prioritizing interface development. 
They discussed reviewing Knight XML documentation and separating the display module from other 
components while focusing mainly on offline processing.
"""

# -------- ROUGE --------

scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],
    use_stemmer=True
)

scores = scorer.score(reference_summary, generated_summary)

print("ROUGE Scores:")
for key, value in scores.items():
    print(f"{key}: {value}")

# -------- BLEU --------

reference_tokens = [reference_summary.split()]
candidate_tokens = generated_summary.split()

bleu_score = sentence_bleu(reference_tokens, candidate_tokens)

print("\nBLEU Score:", bleu_score)