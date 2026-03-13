# prompts.py

def general_prompt(transcript: str) -> str:
    return f"""
You are an AI meeting assistant.

The transcript below contains speaker labels and timestamps.

Provide a structured summary:

1. Meeting Overview (2-3 sentences)
2. Key Discussion Points (bullet points)
3. Decisions Made
4. Action Items (include speaker names if available)

Do NOT hallucinate.
Use only information present in transcript.

Transcript:
{transcript}
"""


def technical_prompt(transcript: str) -> str:
    return f"""
You are a technical meeting summarizer.

Extract and summarize:

- Technical topics discussed
- Architecture/design decisions
- Risks/issues identified
- Implementation next steps

Transcript:
{transcript}
"""


def standup_prompt(transcript: str) -> str:
    return f"""
Summarize the standup meeting.

For each speaker include:
- Yesterday's work
- Today's plan
- Blockers

Transcript:
{transcript}
"""
