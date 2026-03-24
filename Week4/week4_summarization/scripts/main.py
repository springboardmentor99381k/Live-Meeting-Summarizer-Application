import os
from load_transcript import load_transcript
from summarize import generate_summary

INPUT_FILE = "../../Week3/week3_diarization/transcript.txt"
OUTPUT_FILE = "../outputs/meeting_summary.txt"


def main():

    print("Loading transcript...")
    transcript = load_transcript(INPUT_FILE)

    print("Generating structured summary...")

    summary, key_points, decisions, actions = generate_summary(transcript)

    final_output = f"""
MEETING SUMMARY
---------------
{summary}

KEY POINTS
----------
{key_points}

DECISIONS
---------
{decisions}

ACTION ITEMS
------------
{actions}
"""

    print(final_output)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_output)

    print("\nStructured summary saved successfully!")


if __name__ == "__main__":
    main()