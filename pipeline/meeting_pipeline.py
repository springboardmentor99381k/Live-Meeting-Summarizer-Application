import os
from diarization.diarize import SpeakerDiarization
from summarization.summarizer import summarize_text


class MeetingPipeline:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        self.diarizer = SpeakerDiarization(hf_token)

    @staticmethod
    def _find_speaker(annotation, start_time, end_time):
        best_speaker = "UNKNOWN"
        best_overlap = 0.0

        for turn, _, speaker in annotation.itertracks(yield_label=True):
            overlap_start = max(start_time, turn.start)
            overlap_end = min(end_time, turn.end)
            overlap = max(0.0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = speaker

        return best_speaker

    def run(self, whisper_result, audio_file):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"{audio_file} not found")

        diarize_output = self.diarizer.diarize(audio_file)
        annotation = diarize_output.speaker_diarization

        diarized_lines = []
        merged_text = []

        for seg in whisper_result["segments"]:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()

            if not text:
                continue

            speaker = self._find_speaker(annotation, start, end)
            line = f"[{speaker}] {text}"

            diarized_lines.append(line)
            merged_text.append(line)

        diarized_transcript = "\n".join(diarized_lines)

        clean_text_for_summary = "\n".join(merged_text).replace(
            "Structured conversation for a weekly team meeting focused on a project update.",
            ""
        )

        summary = summarize_text(clean_text_for_summary)

        return {
            "diarized_transcript": diarized_transcript,
            "summary": summary
        }