from pathlib import Path

from .diarization import run_diarization
from .summarizer import generate_summary
from .transcription import transcribe_audio


def _find_speaker_for_time(time: float, speaker_segments):
    """Return the speaker label for a given timestamp based on diarization segments."""
    if not speaker_segments:
        return None

    for segment in speaker_segments:
        start = segment.get("start", 0.0)
        end = segment.get("end", 0.0)
        if start <= time < end:
            return segment.get("speaker")

    return None


def _merge_speaker_labels(transcript_segments, speaker_segments):
    """Merge Whisper transcript segments with speaker labels from pyannote."""
    if not transcript_segments or not speaker_segments:
        return ""

    lines = []
    for segment in transcript_segments:
        start = segment.get("start", 0.0)
        text = segment.get("text", "").strip()
        speaker_label = _find_speaker_for_time(start, speaker_segments) or "Speaker"
        lines.append(f"{speaker_label}: {text}")

    return "\n".join(lines)


def run_pipeline(audio_file: str):
    print("Starting backend pipeline...")

    result = transcribe_audio(audio_file)
    if not result or not result.get("text"):
        print("Pipeline stopped due to transcription failure")
        return

    speaker_segments = run_diarization(audio_file)
    if not speaker_segments:
        print("Pipeline stopped due to diarization failure")
        return

    diarized_text = _merge_speaker_labels(result.get("segments", []), speaker_segments)

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Save the diarized transcript (Speaker X: text)
    with open(outputs_dir / "diarized_transcript.txt", "w", encoding="utf-8") as f:
        f.write(diarized_text)

    # Generate a summary from the diarized transcript if available.
    summary_source = diarized_text or result.get("text", "")
    summary = generate_summary(summary_source)
    if not summary:
        print("Pipeline stopped due to summarization failure")
        return

    print("Pipeline completed")
