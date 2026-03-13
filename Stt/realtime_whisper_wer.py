import whisper
import sounddevice as sd
import numpy as np
import queue
import time
from jiwer import wer

SAMPLE_RATE = 16000
CHUNK_SECONDS = 5
RECORD_SECONDS = 30

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

def main():
    print("Loading Whisper model...")
    model = whisper.load_model("tiny")

    print(f"\n🎤 Live transcription started ({RECORD_SECONDS} seconds)...\n")

    start_time = time.time()
    chunk_samples = SAMPLE_RATE * CHUNK_SECONDS
    buffer = np.empty((0, 1), dtype="float32")

    full_transcript = []

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback,
    ):
        while time.time() - start_time < RECORD_SECONDS:
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data), axis=0)

            if len(buffer) >= chunk_samples:
                audio_chunk = buffer[:chunk_samples]
                buffer = buffer[chunk_samples:]

                audio_np = audio_chunk.flatten()

                result = model.transcribe(audio_np, fp16=False)
                text = result["text"].strip()

                if text:
                    print("📝", text)
                    full_transcript.append(text)

    print("\n🛑 Live transcription finished")

    whisper_output = " ".join(full_transcript)

    print("\n--- FINAL WHISPER TRANSCRIPT ---")
    print(whisper_output)

    reference = input("\n✍️ Type what you actually said:\n")

    error = wer(reference.lower(), whisper_output.lower())

    print(f"\n📊 WER: {error * 100:.2f}%")

    if error <= 0.15:
        print("✅ WER < 15% (GOOD)")
    else:
        print("❌ WER > 15% (Needs improvement)")

if __name__ == "__main__":
    main()