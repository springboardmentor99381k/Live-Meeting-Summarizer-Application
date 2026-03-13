from faster_whisper import WhisperModel
import numpy as np
from audio_stream import start_stream, audio_queue, samplerate

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="float32"
)

buffer_audio = b""
bytes_per_sec = samplerate * 2
buffer_duration = 4  # slightly longer for stability

whisper_transcript = []

print("🎙️ Whisper live transcription — Ctrl+C to stop")

with start_stream():
    try:
        while True:
            buffer_audio += audio_queue.get()

            if len(buffer_audio) > buffer_duration * bytes_per_sec:
                audio_np = np.frombuffer(
                    buffer_audio, dtype=np.int16
                ).astype(np.float32) / 32768.0

                buffer_audio = b""

                segments, _ = model.transcribe(
                    audio_np,
                    language="en",
                    beam_size=5
                )

                for seg in segments:
                    print("WHISPER:", seg.text)
                    whisper_transcript.append(seg.text)

    except KeyboardInterrupt:
        print("\nStopped")

with open("logs/whisper_log.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(whisper_transcript))