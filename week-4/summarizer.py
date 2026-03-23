import json
from groq import Groq

client = Groq(api_key="groq_api_key")


def summarize_transcript(transcript):

    prompt = f"""
You are an AI meeting assistant.

Summarize the meeting transcript.

Requirements:
- Preserve speaker contributions
- Identify key discussion points
- Extract action items
- Highlight technical decisions

Output format:

Meeting Overview:
Key Discussion Points:
Speaker Contributions:
Action Items:
Decisions:

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# Load diarization output JSON
with open("diarized_output.json", "r") as f:
    data = json.load(f)

transcript = data["readable_transcript"]

summary = summarize_transcript(transcript)

print("\n===== MEETING SUMMARY =====\n")
print(summary)