def merge_transcript_and_speakers(transcript, diarization):

    merged_output = []

    for segment in transcript:

        start = segment["start"]
        text = segment["text"]

        speaker_label = "UNKNOWN"

        for turn, _, speaker in diarization.itertracks(yield_label=True):

            if turn.start <= start <= turn.end:
                speaker_label = speaker
                break

        line = f"{speaker_label}: {text}"
        merged_output.append(line)

    return merged_output