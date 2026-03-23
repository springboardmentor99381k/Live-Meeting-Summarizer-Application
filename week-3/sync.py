# sync.py

def get_word_timestamps_whisper(wav_path: str) -> list:
    """
    Get word-level timestamps from Whisper.
    Returns: [{word, start, end}, ...]
    """
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(wav_path, word_timestamps=True)
    
    words = []
    for segment in result["segments"]:
        for word_info in segment.get("words", []):
            words.append({
                "word": word_info["word"].strip(),
                "start": word_info["start"],
                "end": word_info["end"]
            })
    return words


def assign_speaker_to_words(words: list, diarization_segments: list) -> list:
    """
    Assign speaker label to each word based on time overlap.
    """
    labeled_words = []
    for word in words:
        word_mid = (word["start"] + word["end"]) / 2  # midpoint of word
        speaker = "UNKNOWN"
        
        for seg in diarization_segments:
            if seg["start"] <= word_mid <= seg["end"]:
                speaker = seg["speaker"]
                break
        
        labeled_words.append({**word, "speaker": speaker})
    
    return labeled_words


def build_readable_transcript(labeled_words: list) -> str:
    """
    Group consecutive words by same speaker into turns.
    Output format:
      [Speaker 1]: Let's discuss next quarter goals.
      [Speaker 2]: We should increase sales by 20%.
    """
    if not labeled_words:
        return ""

    transcript_lines = []
    current_speaker = labeled_words[0]["speaker"]
    current_words = []

    # Map SPEAKER_00 → Speaker 1, SPEAKER_01 → Speaker 2, etc.
    speaker_map = {}
    speaker_counter = 1

    for item in labeled_words:
        spk = item["speaker"]
        if spk not in speaker_map:
            speaker_map[spk] = f"Speaker {speaker_counter}"
            speaker_counter += 1

        if spk == current_speaker:
            current_words.append(item["word"])
        else:
            # Save previous speaker's turn
            line = f"[{speaker_map[current_speaker]}]: {' '.join(current_words).strip()}"
            transcript_lines.append(line)
            # Start new turn
            current_speaker = spk
            current_words = [item["word"]]

    # Add last turn
    if current_words:
        line = f"[{speaker_map[current_speaker]}]: {' '.join(current_words).strip()}"
        transcript_lines.append(line)

    return "\n".join(transcript_lines)