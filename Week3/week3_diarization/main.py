from diarization import run_diarization
from transcription import run_transcription
from merge import merge_speaker_text

AUDIO_FILE = "short.wav"

print("Step 1: Transcription")
stt_segments = run_transcription(AUDIO_FILE)

print("Step 2: Diarization")
diar_segments = run_diarization(AUDIO_FILE)

print("Step 3: Merging")
final_output = merge_speaker_text(diar_segments, stt_segments)

print("\nFinal Speaker-wise Transcript:\n")

for item in final_output:
    print(f"{item['speaker']}: {item['text']}")