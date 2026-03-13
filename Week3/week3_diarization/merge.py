def merge_speaker_text(diar_segments, stt_segments):
    final_output = []

    for stt in stt_segments:
        stt_start = stt["start"]
        stt_end = stt["end"]
        text = stt["text"]

        for diar in diar_segments:
            if stt_start >= diar["start"] and stt_end <= diar["end"]:
                final_output.append({
                    "speaker": diar["speaker"],
                    "text": text
                })
                break

    return final_output