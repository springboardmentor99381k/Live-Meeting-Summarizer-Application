from pathlib import Path
from transformers import pipeline


def generate_summary(text: str) -> str:
    """Generate a meeting summary from the provided text."""
    try:
        print("Generating summary...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary_text = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

        formatted_summary = f"""Meeting Summary

Key Points:
• {summary_text}

Action Items:
• 

Short Summary:
{summary_text}
"""
        outputs_dir = Path("outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        with open(outputs_dir / "summary.txt", "w", encoding="utf-8") as f:
            f.write(formatted_summary)

        print("Summary saved successfully.")
        return formatted_summary
    except Exception as e:
        print(f"Summarization failed: {e}")
        return ""