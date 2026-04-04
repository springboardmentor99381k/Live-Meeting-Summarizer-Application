from transformers import pipeline

summarizer = pipeline(
    "text-generation",
    model="gpt2"
)

def summarize_text(text):

    prompt = f"Summarize this meeting:\n{text}\nSummary:"

    result = summarizer(
        prompt,
        max_length=100,
        num_return_sequences=1
    )

    return result[0]["generated_text"]