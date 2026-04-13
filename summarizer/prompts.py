"""
Prompt templates for different meeting types
"""

def general_meeting_prompt(transcript):
    prompt = f"""
You are an AI assistant that summarizes meeting transcripts.

Instructions:
- Preserve speaker structure.
- Extract key decisions.
- Extract important discussion points.
- Write concise bullet points.

Transcript:
{transcript}

Summary:
"""
    return prompt


def project_meeting_prompt(transcript):
    prompt = f"""
Summarize the following project meeting.

Focus on:
- Tasks assigned
- Deadlines
- Important decisions

Transcript:
{transcript}

Summary:
"""
    return prompt


def standup_meeting_prompt(transcript):
    prompt = f"""
Summarize the standup meeting.

Include:
- What was done yesterday
- What will be done today
- Any blockers

Transcript:
{transcript}

Summary:
"""
    return prompt