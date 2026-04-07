from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "facebook/bart-large-cnn"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def summarize_text(text):
    text = text.strip()
    if not text:
        return "No content to summarize."

    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=120,
            min_new_tokens=40,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)