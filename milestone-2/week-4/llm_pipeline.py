# llm_pipeline.py

import os
from prompt_templates import general_prompt, technical_prompt, standup_prompt
from groq_summarizer import GroqSummarizer
from evaluation_llm import evaluate_summary


def load_transcript(file_path="results/diarized.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_summary(summary_text):
    with open("results/summary.txt", "w", encoding="utf-8") as f:
        f.write(summary_text)


def save_evaluation(scores):
    with open("results/evaluation_scores.txt", "w", encoding="utf-8") as f:
        for key, value in scores.items():
            f.write(f"{key}: {value}\n")


def choose_prompt(meeting_type, transcript):

    if meeting_type == "technical":
        return technical_prompt(transcript)
    elif meeting_type == "standup":
        return standup_prompt(transcript)
    else:
        return general_prompt(transcript)


def run_llm_pipeline(meeting_type="general"):

    print("Loading transcript...")
    transcript = load_transcript()

    print("Generating prompt...")
    prompt = choose_prompt(meeting_type, transcript)

    print("Calling Groq LLaMA model...")
    summarizer = GroqSummarizer()
    summary = summarizer.summarize(prompt)

    print("Saving summary...")
    save_summary(summary)

    # Optional evaluation if reference exists
    reference_path = "results/reference_summary.txt"

    if os.path.exists(reference_path):
        print("Evaluating summary...")
        with open(reference_path, "r", encoding="utf-8") as f:
            reference = f.read()

        scores = evaluate_summary(reference, summary)
        save_evaluation(scores)

        print("Evaluation Scores:", scores)

    print("Pipeline completed successfully.")
