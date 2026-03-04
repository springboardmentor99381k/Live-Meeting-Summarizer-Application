from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

with open("transcripts/whisper/meeting.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("Generating summary...")

summary = summarizer(
    text[:4000],
    max_length=150,
    min_length=60,
    do_sample=False
)

summary_text = summary[0]["summary_text"]

with open("summaries/meeting_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary_text)

print("Summary saved to summaries/meeting_summary.txt")