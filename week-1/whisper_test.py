import whisper
import shutil
import sys

# verify ffmpeg exists
if shutil.which("ffmpeg") is None:
    sys.stderr.write("ERROR: ffmpeg executable not found.\n")
    sys.stderr.write("Please install ffmpeg and make sure it is on your PATH.\n")
    sys.exit(1)

model = whisper.load_model("base")

input_path = "amicorpus/EN2001a/audio/EN2001a.Mix-Headset.wav"

try:
    result = model.transcribe(input_path)
except FileNotFoundError as exc:
    sys.stderr.write(f"transcribe failed: {exc}\n")
    raise

with open("whisper_output.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("Transcription saved to whisper_output.txt")