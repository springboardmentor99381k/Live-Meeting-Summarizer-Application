def create_diarized_transcript(transcript, segments):

    # ✅ CRITICAL SAFETY
    if not segments:
        return "[Speaker 1]: " + transcript

    words = transcript.split()
    chunk_size = max(1, len(words) // len(segments))

    diarized = ""
    index = 0

    for seg in segments:
        speaker = seg["speaker"]
        chunk = words[index:index + chunk_size]
        index += chunk_size

        diarized += f"[{speaker}]: {' '.join(chunk)}\n"

    return diarized