from diarization.diarize import SpeakerDiarization
import whisper
import os
from summarization.summarizer import summarize_text

HF_TOKEN = os.getenv("HF_TOKEN")

def find_speaker(annotation, start_time, end_time):
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

if __name__ == "__main__":
    audio_file = "processed.wav"

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"{audio_file} not found")

    diarizer = SpeakerDiarization(HF_TOKEN)
    diarize_output = diarizer.diarize(audio_file)
    annotation = diarize_output.speaker_diarization

    model = whisper.load_model("base")
    whisper_output = model.transcribe(
        audio_file,
        fp16=False
    )

    print("\n🧑‍🤝‍🧑 Speaker + Text:\n")

    full_text = ""

    for seg in whisper_output["segments"]:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip()

        speaker = find_speaker(annotation, start, end)
        print(f"[{speaker}] {text}")

        full_text += f"[{speaker}] {text}\n"

    clean_text_for_summary = full_text.replace(
        "Structured conversation for a weekly team meeting focused on a project update.", ""
    )

    print("\n📄 SUMMARY:\n")
    print(summarize_text(clean_text_for_summary))