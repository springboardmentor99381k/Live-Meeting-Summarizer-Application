
import whisper
import os
import torch
from pyannote.audio import Pipeline



AUDIO_PATH = "ES2002a/audio/ES2002a.Mix-Headset.wav"

# Create output folder
os.makedirs("Data", exist_ok=True)

# Check if audio file exists
if not os.path.exists(AUDIO_PATH):
    print("Audio file not found!")
    exit()


print("Loading speaker diarization model...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=True,
    revision="2.1"
)

# Use GPU if available
if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))
    print("Using GPU")
else:
    print("Using CPU")

print("Running speaker diarization...\n")

diarization = pipeline(AUDIO_PATH)


print("Loading Whisper model...")

model = whisper.load_model("small")

print("Transcribing audio...\n")

result = model.transcribe(AUDIO_PATH)

stt_segments = result["segments"]


print("Generating diarized transcript...\n")

diarized_output = []

for seg in stt_segments:

    start = seg["start"]
    end = seg["end"]
    text = seg["text"].strip()

    speaker_label = "Unknown"

    for turn, _, speaker in diarization.itertracks(yield_label=True):

        if start >= turn.start and end <= turn.end:
            speaker_label = speaker
            break

    diarized_output.append(
        f"[{speaker_label}] ({start:.2f}-{end:.2f}): {text}"
    )


print("===== DIARIZED TRANSCRIPT =====\n")

for line in diarized_output[:20]:
    print(line)

output_file = "Data/diarized_transcript.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for line in diarized_output:
        f.write(line + "\n")

print(f"\nTranscript saved to {output_file}")