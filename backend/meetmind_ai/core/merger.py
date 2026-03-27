import re
from typing import Any, Dict, List, Optional


class Merger:
    """Merge transcript text with diarization speaker segments."""

    def __init__(self, transcript: str, segments: List[Dict[str, Any]]):
        self.transcript = transcript or ""
        self.segments = segments or []

    def merge(self) -> List[Dict[str, Any]]:
        """
        Align transcript with diarization segments.

        Returns:
            List of dicts:
            [{"speaker": "SPEAKER_00", "text": "...", "start": 0.0, "end": 3.5}, ...]
        """
        if not self.segments:
            return []

        normalized_segments = self._normalize_segments(self.segments)
        timed_utterances = self._extract_timed_utterances(self.transcript)

        if timed_utterances:
            return self._merge_with_timestamps(normalized_segments, timed_utterances)

        return self._merge_without_timestamps(normalized_segments, self.transcript)

    def format_transcript(self, merged: List[Dict[str, Any]]) -> str:
        """Convert merged output into readable multi-line transcript."""
        if not merged:
            return ""

        lines: List[str] = []
        for item in merged:
            speaker = str(item.get("speaker", "UNKNOWN"))
            text = str(item.get("text", "")).strip()
            start = float(item.get("start", 0.0))
            end = float(item.get("end", 0.0))
            lines.append(
                f"{speaker} [{self._format_time(start)} - {self._format_time(end)}]: {text}"
            )

        return "\n".join(lines)

    def get_speaker_map(self, merged: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map speaker IDs to simple display names in order of first appearance."""
        speaker_map: Dict[str, str] = {}
        speaker_count = 0

        for item in merged:
            speaker = str(item.get("speaker", "UNKNOWN"))
            if speaker not in speaker_map:
                speaker_count += 1
                speaker_map[speaker] = f"Speaker {speaker_count}"

        return speaker_map

    def _normalize_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []

        for segment in segments:
            try:
                speaker = str(segment["speaker"])
                start = float(segment["start"])
                end = float(segment["end"])
                if end < start:
                    start, end = end, start
                normalized.append(
                    {
                        "speaker": speaker,
                        "start": start,
                        "end": end,
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

        normalized.sort(key=lambda x: x["start"])
        return normalized

    def _merge_with_timestamps(
        self,
        segments: List[Dict[str, Any]],
        utterances: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        bucket: Dict[int, List[str]] = {i: [] for i in range(len(segments))}

        for utterance in utterances:
            text = utterance.get("text", "").strip()
            if not text:
                continue

            best_index = self._find_best_segment_index(
                segments,
                float(utterance.get("start", 0.0)),
                float(utterance.get("end", 0.0)),
            )
            if best_index is None:
                continue

            bucket[best_index].append(text)

        merged: List[Dict[str, Any]] = []
        for i, segment in enumerate(segments):
            joined = " ".join(bucket[i]).strip()
            if not joined:
                continue
            merged.append(
                {
                    "speaker": segment["speaker"],
                    "text": joined,
                    "start": segment["start"],
                    "end": segment["end"],
                }
            )

        return merged

    def _merge_without_timestamps(
        self,
        segments: List[Dict[str, Any]],
        transcript: str,
    ) -> List[Dict[str, Any]]:
        words = transcript.split()
        if not words:
            return []

        durations = [max(0.0, s["end"] - s["start"]) for s in segments]
        total_duration = sum(durations)

        if total_duration <= 0:
            total_duration = float(len(segments))
            durations = [1.0 for _ in segments]

        assigned_counts = [0 for _ in segments]
        remaining_words = len(words)

        # Assign words proportionally to segment duration.
        for i, duration in enumerate(durations):
            if i == len(segments) - 1:
                count = remaining_words
            else:
                ratio = duration / total_duration if total_duration > 0 else 0.0
                count = int(round(ratio * len(words)))
                count = max(0, min(count, remaining_words))

            assigned_counts[i] = count
            remaining_words -= count

        # Correct rounding drift by distributing leftovers to nearest non-empty durations.
        idx = 0
        while remaining_words > 0 and segments:
            assigned_counts[idx % len(segments)] += 1
            remaining_words -= 1
            idx += 1

        merged: List[Dict[str, Any]] = []
        cursor = 0
        for i, segment in enumerate(segments):
            count = assigned_counts[i]
            if count <= 0:
                continue

            text = " ".join(words[cursor : cursor + count]).strip()
            cursor += count
            if not text:
                continue

            merged.append(
                {
                    "speaker": segment["speaker"],
                    "text": text,
                    "start": segment["start"],
                    "end": segment["end"],
                }
            )

        return merged

    def _find_best_segment_index(
        self,
        segments: List[Dict[str, Any]],
        utt_start: float,
        utt_end: float,
    ) -> Optional[int]:
        if not segments:
            return None

        if utt_end < utt_start:
            utt_start, utt_end = utt_end, utt_start

        best_index = None
        best_overlap = 0.0

        for i, seg in enumerate(segments):
            seg_start = float(seg["start"])
            seg_end = float(seg["end"])
            overlap = max(0.0, min(utt_end, seg_end) - max(utt_start, seg_start))

            if overlap > best_overlap:
                best_overlap = overlap
                best_index = i

        if best_index is not None and best_overlap > 0:
            return best_index

        # No overlap: assign to nearest segment midpoint.
        utt_mid = (utt_start + utt_end) / 2.0
        nearest_index = 0
        nearest_distance = float("inf")

        for i, seg in enumerate(segments):
            seg_mid = (float(seg["start"]) + float(seg["end"])) / 2.0
            distance = abs(seg_mid - utt_mid)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_index = i

        return nearest_index

    def _extract_timed_utterances(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Parse timestamped transcript lines.

        Supported examples:
            [0:00 - 0:03] Hello there
            [00:00:01.2 - 00:00:04.8] Hello there
            0.0 --> 2.5 Hello there
        """
        if not transcript:
            return []

        utterances: List[Dict[str, Any]] = []
        lines = [line.strip() for line in transcript.splitlines() if line.strip()]

        bracket_pattern = re.compile(
            r"^\[(?P<start>[^\]]+?)\s*-\s*(?P<end>[^\]]+?)\]\s*(?P<text>.+)$"
        )
        arrow_pattern = re.compile(
            r"^(?P<start>[0-9:.]+)\s*-->\s*(?P<end>[0-9:.]+)\s*(?P<text>.+)$"
        )

        for line in lines:
            match = bracket_pattern.match(line) or arrow_pattern.match(line)
            if not match:
                continue

            start_raw = match.group("start")
            end_raw = match.group("end")
            text = match.group("text").strip()

            start = self._parse_time_to_seconds(start_raw)
            end = self._parse_time_to_seconds(end_raw)

            if start is None or end is None or not text:
                continue

            utterances.append({"start": start, "end": end, "text": text})

        return utterances

    def _parse_time_to_seconds(self, value: str) -> Optional[float]:
        text = value.strip()

        if re.match(r"^\d+(\.\d+)?$", text):
            return float(text)

        parts = text.split(":")
        try:
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            return None

        return None

    def _format_time(self, seconds: float) -> str:
        total_seconds = max(0, int(round(seconds)))
        hours, rem = divmod(total_seconds, 3600)
        minutes, secs = divmod(rem, 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
