import queue
import sounddevice as sd
import numpy as np
import whisper
import torch
from pyannote.audio import Pipeline
import tempfile
import wave

SAMPLE_RATE = 16000
CHUNK_SEC = 4

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def save_wav(audio, filename):
    with wave.open(filename, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio.tobytes())

def realtime_diarization(hf_token):

    print("Loading models")

    whisper_model = whisper.load_model("base")

    diar_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=hf_token
    )

    if torch.cuda.is_available():
        diar_pipeline.to(torch.device("cuda"))

    print("Listening")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback
    ):

        buffer = []

        while True:
            data = audio_queue.get()
            buffer.append(data)

            if len(buffer) * len(data) >= SAMPLE_RATE * CHUNK_SEC:

                audio = np.concatenate(buffer)
                buffer = []

                with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                    save_wav(audio, tmp.name)

                    result = whisper_model.transcribe(tmp.name)
                    diar = diar_pipeline(tmp.name)

                    print("\nChunk Result")

                    for turn, _, speaker in diar.itertracks(yield_label=True):
                        text = ""
                        for seg in result["segments"]:
                            if seg["start"] >= turn.start and seg["end"] <= turn.end:
                                text += seg["text"] + " "

                        if text.strip():
                            print(speaker + ": " + text.strip())



import os
import queue
import torch
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from pyannote.audio import Pipeline

load_dotenv()

# Audio settings
SAMPLE_RATE = 16000
CHUNK_DURATION = 5  # seconds
BUFFER_SIZE = SAMPLE_RATE * CHUNK_DURATION

audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


class RealTimeDiarization:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in .env file")

        print("Loading pyannote diarization model...")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token
        )

        self.pipeline.to(torch.device(self.device))
        print("Model loaded!\n")

        self.buffer = np.empty((0, 1), dtype=np.float32)

    def process_audio(self):
        print("🎤 Listening... Press Ctrl+C to stop.\n")

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            callback=audio_callback
        ):
            while True:
                chunk = audio_queue.get()
                self.buffer = np.vstack((self.buffer, chunk))

                if len(self.buffer) >= BUFFER_SIZE:
                    self.run_diarization(self.buffer[:BUFFER_SIZE])
                    self.buffer = self.buffer[BUFFER_SIZE:]

    def run_diarization(self, audio_chunk):
        waveform = torch.from_numpy(audio_chunk.T)

        diarization = self.pipeline({
            "waveform": waveform,
            "sample_rate": SAMPLE_RATE
        })

        print("\n--- Speaker Segments ---")

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            print(
                f"{speaker}: "
                f"{turn.start:.2f}s - {turn.end:.2f}s"
            )


if __name__ == "__main__":
    rt = RealTimeDiarization()
    rt.process_audio()
