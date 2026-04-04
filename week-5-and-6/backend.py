import os
import queue
import threading
import numpy as np
try:
    import sounddevice as sd
except OSError:
    sd = None
    print("Warning: sounddevice or PortAudio not found. Server-side recording will be disabled.")

import soundfile as sf
import whisper
import torch
import warnings
import json
from pyannote.audio import Pipeline
from groq import Groq

warnings.filterwarnings("ignore", message=".*torchcodec is not installed correctly.*")
warnings.filterwarnings("ignore", message=".*degrees of freedom is <= 0.*")

class STTDiarizationSummarizer:
    def __init__(self, hf_token=None, groq_key=None):
        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        
        self.is_recording = False
        self.audio_data = [] # Buffer for raw audio streams
        
        print("Loading Whisper model (tiny.en)...")
        self.whisper_model = whisper.load_model("tiny.en") 
        
        self.hf_token = hf_token or os.environ.get("HF_TOKEN", "hf_token")
        self.groq_key = groq_key or os.environ.get("GROQ_API_KEY", "groq_token")
        
        self.diarization_pipeline = None

        self.samplerate = 16000
        self.channels = 1
        
        self.worker_thread = None
        self.stream = None

    def start_recording(self):
        if sd is None:
            print("Error: Server-side recording is not supported on this device.")
            self.transcript_queue.put("Error: Server-side recording is not supported in this environment (e.g. Render). Please try uploading an audio file instead.")
            return

        self.is_recording = True
        self.audio_data = []
        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            self.audio_queue.put(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            callback=audio_callback,
            blocksize=int(self.samplerate * 0.5)
        )
        self.stream.start()
        
        self.worker_thread = threading.Thread(target=self._realtime_stt_worker, daemon=True)
        self.worker_thread.start()

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if self.worker_thread:
            self.worker_thread.join()
        
        wav_path = "meeting_audio.wav"
        if self.audio_data:
            full_audio = np.concatenate(self.audio_data, axis=0)
        else:
            full_audio = np.zeros((0, 1), dtype=np.float32)
            
        sf.write(wav_path, full_audio, self.samplerate)
        duration_minutes = len(full_audio) / self.samplerate / 60.0
        return wav_path, round(duration_minutes)

    def _realtime_stt_worker(self):
        buffer = np.empty((0, 1), dtype=np.float32)
        chunk_samples = self.samplerate * 5
        
        while self.is_recording or not self.audio_queue.empty():
            try:
                data = self.audio_queue.get(timeout=0.5)
                self.audio_data.append(data)
                buffer = np.concatenate((buffer, data))
                
                if len(buffer) >= chunk_samples:
                    audio_flat = buffer.flatten()
                    result = self.whisper_model.transcribe(
                        audio_flat,
                        language="en",
                        initial_prompt="Live meeting summarizer app.",
                        fp16=torch.cuda.is_available()
                    )
                    text = result["text"].strip()
                    if text:
                        self.transcript_queue.put(text)
                    buffer = buffer[-self.samplerate:]
            except queue.Empty:
                pass


    def run_post_processing(self, wav_path):
        try:
            yield {"status": "Getting word timestamps...", "step": "Transcribing"}
            full_result = self.whisper_model.transcribe(
                wav_path,
                word_timestamps=False,
                language="en",
                initial_prompt="Live meeting summarizer app.",
                fp16=torch.cuda.is_available()
            )
            
            words = []
            for segment in full_result.get("segments", []):
                words.append({
                    "word": segment.get("text", "").strip(),
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0)
                })
            
            yield {"status": f"Running diarization... ({len(words)} words found)", "step": "Diarizing"}
            if not self.diarization_pipeline and self.hf_token:
                try:
                    self.diarization_pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization-3.1",
                        token=self.hf_token
                    )
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    self.diarization_pipeline.to(device)
                except Exception as e:
                    yield {"error": f"Failed to load Pyannote with token. Check permissions: {e}. Using Default."}
            
            if not self.diarization_pipeline:
                diarization_segments = [{"start": 0.0, "end": 999999.0, "speaker": "SPEAKER_00"}]
            else:
                waveform_np, sr = sf.read(wav_path, dtype='float32', always_2d=True)
                waveform_tensor = torch.from_numpy(waveform_np.T)
                audio_dict = {"waveform": waveform_tensor, "sample_rate": sr}
                
                diarization = self.diarization_pipeline(audio_dict)
                    
                diarization_segments = []
                
                target_obj = None
                if hasattr(diarization, 'itertracks'):
                    target_obj = diarization
                elif hasattr(diarization, 'exclusive_speaker_diarization'):
                    target_obj = diarization.exclusive_speaker_diarization
                elif hasattr(diarization, 'speaker_diarization'):
                    target_obj = diarization.speaker_diarization
                else:
                    target_obj = diarization
                    
                if target_obj:
                    for turn, _, speaker in target_obj.itertracks(yield_label=True):
                        diarization_segments.append({
                            "start": round(turn.start, 2),
                            "end": round(turn.end, 2),
                            "speaker": speaker
                        })

            yield {"status": "Merging diarization and transcripts...", "step": "Diarizing"}
            labeled_words = []
            for w in words:
                word_mid = (w["start"] + w["end"]) / 2
                speaker = "UNKNOWN"
                for seg in diarization_segments:
                    if seg["start"] <= word_mid <= seg["end"]:
                        speaker = seg["speaker"]
                        break
                labeled_words.append({**w, "speaker": speaker})
                
            transcript_turns = []
            if labeled_words:
                current_spk = labeled_words[0]["speaker"]
                current_wds = [labeled_words[0]["word"]]
                spk_start = labeled_words[0]["start"]
                spk_map = {}
                spk_cnt = 1
                
                if current_spk not in spk_map:
                    spk_map[current_spk] = f"Speaker {spk_cnt}"
                    spk_cnt += 1
                    
                for item in labeled_words[1:]:
                    spk = item["speaker"]
                    if spk not in spk_map:
                        spk_map[spk] = f"Speaker {spk_cnt}"
                        spk_cnt += 1
                    
                    if spk == current_spk:
                        current_wds.append(item["word"])
                    else:
                        minutes = int(spk_start // 60)
                        seconds = int(spk_start % 60)
                        transcript_turns.append({
                            "speaker": spk_map.get(current_spk, current_spk),
                            "time": f"{minutes:02}:{seconds:02}",
                            "text": ' '.join(current_wds)
                        })
                        current_spk = spk
                        current_wds = [item["word"]]
                        spk_start = item["start"]
                
                if current_wds:
                    minutes = int(spk_start // 60)
                    seconds = int(spk_start % 60)
                    transcript_turns.append({
                        "speaker": spk_map.get(current_spk, current_spk),
                        "time": f"{minutes:02}:{seconds:02}",
                        "text": ' '.join(current_wds)
                    })

            # Calculate speaker participation metrics
            speaker_stats = {}
            total_words = 0
            for turn in transcript_turns:
                spk = turn["speaker"]
                if spk not in speaker_stats:
                    speaker_stats[spk] = {"turns": 0, "words": 0}
                words_cnt = len(turn["text"].split())
                speaker_stats[spk]["turns"] += 1
                speaker_stats[spk]["words"] += words_cnt
                total_words += words_cnt
                
            analytics = []
            for spk, stats in speaker_stats.items():
                percent = int((stats["words"] / max(total_words, 1)) * 100)
                analytics.append({"speaker": spk, "turns": stats["turns"], "percent": percent})

            yield {"status": "Generating final summary via Groq API...", "step": "Summarizing", "transcript": transcript_turns, "analytics": analytics}
            
            summary_json_parsed = {"summary": "No content to summarize.", "action_items": [], "decisions": []}
            if not self.groq_key:
                summary_json_parsed["summary"] = "Error: GROQ_API_KEY not configured."
            elif words:
                try:
                    client = Groq(api_key=self.groq_key)
                    readable_transcript = "\n".join([f"[{t['speaker']} {t['time']}]: {t['text']}" for t in transcript_turns])
                    prompt = f"""You are an AI meeting assistant.
Summarize the following meeting transcript. You MUST respond with ONLY a valid JSON object. Do not include formatting like markdown or backticks.
Format strictly:
{{
  "summary": "Full paragraph overview...",
  "action_items": ["Action 1", "Action 2"],
  "decisions": ["Decision 1", "Decision 2"]
}}

Transcript:
{readable_transcript}"""
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    content = response.choices[0].message.content.strip()
                    # Sanitize model output to ensure valid JSON format
                    if content.startswith("```"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    summary_json_parsed = json.loads(content)
                except Exception as e:
                    summary_json_parsed["summary"] = f"Error during Groq summarize: {e}"
            
            yield {"status": "Done", "step": "Done", "summary": summary_json_parsed, "transcript": transcript_turns, "analytics": analytics}
            
        except Exception as err:
            yield {"error": f"An unexpected error occurred during processing: {err}"}
