import whisper
import time
from audio_stream import get_audio_chunk

class WhisperEngine:

    def __init__(self, model_size="small"):
        self.model = whisper.load_model(model_size)
        self.predictions = []
        self.latencies = []

    def run_once(self):
        audio = get_audio_chunk()

        start = time.time()
        result = self.model.transcribe(audio, fp16=False)
        latency = time.time() - start

        text = result["text"].strip()

        self.predictions.append(text)
        self.latencies.append(latency)

        print("Transcription >", text)