from transformers import pipeline

# load model once
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


def generate_summary(transcript):

    meeting_summary = summarizer(
        transcript,
        max_length=150,
        min_length=40,
        do_sample=False
    )[0]["summary_text"]

    key_points = summarizer(
        "Extract the key discussion points from this meeting:\n" + transcript,
        max_length=120,
        min_length=30,
        do_sample=False
    )[0]["summary_text"]

    decisions = summarizer(
        "What decisions were made in this meeting:\n" + transcript,
        max_length=120,
        min_length=30,
        do_sample=False
    )[0]["summary_text"]

    action_items = summarizer(
        "List the action items from this meeting:\n" + transcript,
        max_length=120,
        min_length=30,
        do_sample=False
    )[0]["summary_text"]

    return meeting_summary, key_points, decisions, action_items