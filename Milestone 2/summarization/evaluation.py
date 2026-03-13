from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu

# Read reference summary
with open("summarization/reference_summary.txt", "r", encoding="utf-8") as f:
    reference = f.read()

# Read AI generated summary
with open("summarization/summary_copy.txt", "r", encoding="utf-8") as f:
    generated = f.read()

# ROUGE Evaluation
scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
scores = scorer.score(reference, generated)

rouge1 = scores['rouge1'].fmeasure
rouge2 = scores['rouge2'].fmeasure
rougeL = scores['rougeL'].fmeasure

print("\n===== ROUGE Evaluation Results =====")
print(f"ROUGE-1 Score : {rouge1:.3f}")
print(f"ROUGE-2 Score : {rouge2:.3f}")
print(f"ROUGE-L Score : {rougeL:.3f}")

# Check condition
print("\n===== Evaluation Condition Check =====")
if rouge1 > 0.4:
    print("✅ Condition Satisfied: ROUGE-1 > 0.4")
    print("The generated summary meets the required quality level.")
else:
    print("❌ Condition Not Satisfied: ROUGE-1 <= 0.4")
    print("The summary quality needs improvement.")

# BLEU Evaluation
reference_tokens = [reference.split()]
generated_tokens = generated.split()

bleu = sentence_bleu(reference_tokens, generated_tokens)

print("\n===== BLEU Evaluation =====")
print(f"BLEU Score : {bleu:.5f}")