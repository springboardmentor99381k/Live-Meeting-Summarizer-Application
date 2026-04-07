import queue
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper


class RealTimeSTT:
    def __init__(self, model_name="base", samplerate=16000, channels=1, blocksize=8000):
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize

        self.audio_queue = queue.Queue()
        self.audio_chunks = []
        self.live_transcript_segments = []

        self.recording = False
        self.stream = None
        self.worker_thread = None
        self.lock = threading.Lock()

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def start_recording(self):
        self.recording = True
        self.audio_chunks = []
        self.live_transcript_segments = []

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self.audio_callback,
            blocksize=self.blocksize
        )
        self.stream.start()

        self.worker_thread = threading.Thread(target=self._process_live_audio, daemon=True)
        self.worker_thread.start()

    def _process_live_audio(self):
        buffer_chunks = []
        chunk_counter = 0

        while self.recording:
            try:
                data = self.audio_queue.get(timeout=1)
                self.audio_chunks.append(data)
                buffer_chunks.append(data)
                chunk_counter += 1

                # live STT every few chunks
                if chunk_counter >= 4:
                    audio_np = np.concatenate(buffer_chunks, axis=0).flatten().astype(np.float32)

                    try:
                        result = self.model.transcribe(audio_np, fp16=False)
                        text = result["text"].strip()

                        if text:
                            with self.lock:
                                self.live_transcript_segments.append(text)
                    except Exception as e:
                        print(f"Live transcription warning: {e}")

                    buffer_chunks = []
                    chunk_counter = 0

            except queue.Empty:
                continue

    def get_live_transcript(self):
        with self.lock:
            return " ".join(self.live_transcript_segments)

    def stop_recording(self, output_path="processed.wav"):
        self.recording = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

        if self.worker_thread is not None:
            self.worker_thread.join(timeout=2)

        if not self.audio_chunks:
            return {"text": "", "segments": []}, output_path

        full_audio = np.concatenate(self.audio_chunks, axis=0).astype(np.float32)
        sf.write(output_path, full_audio, self.samplerate)

        # IMPORTANT: load a fresh model for final transcription
        final_model = whisper.load_model(self.model_name)

        # IMPORTANT: do not use word_timestamps=True here
        final_result = final_model.transcribe(
            output_path,
            fp16=False
        )

        return final_result, output_path