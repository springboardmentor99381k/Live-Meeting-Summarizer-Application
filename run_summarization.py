from summarizer.summarizer import MeetingSummarizer
from summarizer.evaluate import evaluate_summary


def load_transcript(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_summary(summary):

    with open("outputs/summary_output.txt", "w") as f:
        f.write(summary)


def main():

    transcript = load_transcript("summarizer/sample_transcript.txt")

    summarizer = MeetingSummarizer()

    summary = summarizer.summarize(transcript)

    print("\nGenerated Summary:\n")
    print(summary)

    save_summary(summary)

   
    reference = """
The meeting discussed the development of the live meeting summarizer system.
The Whisper speech-to-text module has been successfully integrated.
The diarization model still requires optimization.
The BART summarization model is used to generate summaries from transcripts.
Further improvements are needed to improve transcription accuracy.
"""

    scores = evaluate_summary(reference, summary)

    print("\nEvaluation Scores:")
    print(scores)


if __name__ == "__main__":
    main()