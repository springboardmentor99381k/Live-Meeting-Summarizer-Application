from .transcription import transcribe_audio
from .diarization import run_diarization
from .merge import merge_transcript_and_speakers

AUDIO_FILE = "short.wav"

print("Step 1: Transcription")
transcript = transcribe_audio(AUDIO_FILE)

print("Step 2: Diarization")
diarization = run_diarization(AUDIO_FILE)

print("Step 3: Merging")
final_transcript = merge_transcript_and_speakers(transcript, diarization)

print("\nFinal Speaker-wise Transcript:\n")

with open("transcript.txt", "w", encoding="utf-8") as f:
    for line in final_transcript:
        print(line)
        f.write(line + "\n")