KEY_POINTS_PROMPT = """
Summarize the following meeting transcript into key discussion points.
Keep it concise and clear.

Transcript:
{transcript}
"""

ACTION_ITEMS_PROMPT = """
From the meeting transcript below, extract action items and responsibilities.

Transcript:
{transcript}
"""

DECISIONS_PROMPT = """
List the key decisions made in the meeting transcript below.

Transcript:
{transcript}
"""