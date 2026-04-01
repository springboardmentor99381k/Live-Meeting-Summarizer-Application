import os

from groq import Groq


def align(whisper_result: dict, speaker_turns: list[dict]) -> str:
    """Assign each Whisper segment to the speaker with the largest overlap."""
    lines: list[str] = []
    previous_speaker = None

    for segment in whisper_result.get("segments", []):
        best_speaker = "Unknown"
        best_overlap = 0.0

        seg_start = float(segment.get("start", 0.0))
        seg_end = float(segment.get("end", 0.0))

        for turn in speaker_turns:
            overlap = max(
                0.0,
                min(seg_end, float(turn["end"])) - max(seg_start, float(turn["start"])),
            )
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = turn["speaker"]

        if best_speaker != previous_speaker:
            lines.append(f"{best_speaker}:")
            previous_speaker = best_speaker

        text = str(segment.get("text", "")).strip()
        if text:
            lines.append(f"  {text}")

    return "\n".join(lines).strip()


def create_prompt(transcript: str) -> str:
    return f"""You are an AI assistant that summarizes meeting transcripts.

Analyze the following meeting transcript and generate a structured summary.

Transcript:
{transcript}

Provide the output in this format:

1. Key Points
2. Decisions Made
3. Action Items
4. Short Summary

Be clear and concise."""


def summarize(transcript: str, config) -> str:
    client = Groq(api_key=config.groq_api_key)
    response = client.chat.completions.create(
        model=config.groq_model,
        messages=[{"role": "user", "content": create_prompt(transcript)}],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def ensure_output_dir(output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
