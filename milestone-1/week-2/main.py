import threading
import time
import keyboard
import wave
import numpy as np
import datetime
from audio_stream import start_stream, recorded_frames
from whisper_engine import WhisperEngine
from evaluation import evaluate

RECORD_TIME = 30
CHUNK_SECONDS = 4
SAMPLE_RATE = 16000


def load_references():
    with open("references.txt") as f:
        return [l.strip() for l in f]


def save_audio(frames):
    if not frames:
        print("No audio captured.")
        return None

    audio_data = np.concatenate(frames, axis=0)

    filename = f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

    return filename


def main():
    engine = WhisperEngine("small")
    stream = start_stream()

    recording_event = threading.Event()
    stop_event = threading.Event()

    def stt_worker():
        while not stop_event.is_set():
            if recording_event.is_set():
                engine.run_once()
            else:
                time.sleep(0.2)

    t = threading.Thread(target=stt_worker)
    t.start()

    with stream:
        print("Press S to start recording")
        print("Press Q to stop early")
        print("Auto stop after 30 seconds")

        started = False
        start_time = 0

        while not stop_event.is_set():

            if keyboard.is_pressed("s") and not started:
                recording_event.set()
                started = True
                start_time = time.time()
                print("Status: Listening")
                time.sleep(0.5)

            if keyboard.is_pressed("q") and started:
                print("Stopped early by user")
                stop_event.set()
                recording_event.clear()
                break

            # if started:
            #     elapsed = time.time() - start_time
            #     if elapsed >= RECORD_TIME:
            #         print("Auto stop after 30 seconds")
            #         stop_event.set()
            #         recording_event.clear()
            #         break

            time.sleep(0.2)

    t.join()

    # Save audio
    filename = save_audio(recorded_frames)
    if filename:
        print("Audio saved as:", filename)

    # Print transcription
    refs = load_references()

    if engine.predictions:
        final_text = " ".join(engine.predictions)
        print("\nFinal Transcription:")
        print(final_text)
    else:
        print("No transcription captured.")
        final_text = ""

    # Evaluate
    evaluate(engine.predictions, refs)

    # Latency + RTF
    if engine.latencies:
        avg_latency = sum(engine.latencies) / len(engine.latencies)
        rtf = avg_latency / CHUNK_SECONDS

        print("Average latency:", round(avg_latency, 3))
        print("Real Time Factor:", round(rtf, 3))


if __name__ == "__main__":
    main()
