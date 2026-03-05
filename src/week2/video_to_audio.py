import subprocess

video_path = "Data/raw/meeting.mp4"
audio_path = "Data/audio/meeting.wav"

command = [
    "ffmpeg",
    "-i", video_path,
    "-ar", "16000",
    "-ac", "1",
    audio_path,
    "-y"
]

print("Extracting audio from video...")
subprocess.run(command)
print("Audio saved to Data/audio/meeting.wav")