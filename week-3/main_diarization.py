# main_diarization.py

import json
from datetime import datetime
from diarization import load_diarization_pipeline, diarize_audio
from sync import get_word_timestamps_whisper, assign_speaker_to_words, build_readable_transcript

HF_TOKEN = "hugging_face_token"
WAV_FILE = "sample.wav"

def run_diarization_pipeline(wav_path: str):
    print("Loading diarization pipeline...")
    pipeline = load_diarization_pipeline(HF_TOKEN)

    import soundfile as sf
    import torch
    w_info = sf.info(wav_path)
    device_str = "GPU" if torch.cuda.is_available() else "CPU"
    #print(f"Running speaker diarization on {device_str} for a {w_info.duration/60:.2f}-minute audio...")
    if not torch.cuda.is_available() and w_info.duration > 300:
        print("Processing audio on CPU")

    diar_segments = diarize_audio(wav_path, pipeline)
    print(f"Found {len(set(s['speaker'] for s in diar_segments))} speakers")

    print("Getting word timestamps from Whisper...")
    words = get_word_timestamps_whisper(wav_path)

    print("Syncing speakers with transcript...")
    labeled_words = assign_speaker_to_words(words, diar_segments)

    print("Building readable transcript...")
    transcript = build_readable_transcript(labeled_words)

    print("\n===== DIARIZED TRANSCRIPT =====\n")
    print(transcript)

    # Save to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "wav_file": wav_path,
        "diarization_segments": diar_segments,
        "labeled_words": labeled_words,
        "readable_transcript": transcript
    }
    with open("diarized_output.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nSaved to diarized_output.json")

    return transcript

if __name__ == "__main__":
    run_diarization_pipeline(WAV_FILE)