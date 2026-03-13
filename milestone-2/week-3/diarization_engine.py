import os
import torch
import whisper
import torchaudio
from dotenv import load_dotenv
from pyannote.audio import Pipeline

load_dotenv()


class DiarizationEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in .env file")

        # Load pyannote diarization pipeline
        print("Loading pyannote diarization model...")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token
        )

        self.pipeline.to(torch.device(self.device))

        # Load Whisper model
        print("Loading Whisper small model...")
        self.whisper_model = whisper.load_model("small")

        print("Models loaded successfully!\n")

    # Transcribe audio
    def transcribe(self, audio_path):
        print("Transcribing...")
        result = self.whisper_model.transcribe(audio_path)

        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })

        return segments

    # Run diarization
    def diarize(self, audio_path):
        print("Running diarization...")

        waveform, sample_rate = torchaudio.load(audio_path)

        # Convert stereo to mono if needed
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        diarization = self.pipeline({
            "waveform": waveform,
            "sample_rate": sample_rate
        })

        annotation = diarization.speaker_diarization

        speaker_segments = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            speaker_segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        return speaker_segments

    # Match speakers with STT segments
    def match_speakers(self, stt_segments, speaker_segments):
        transcript = []
        speaker_map = {}
        speaker_count = 1

        for stt in stt_segments:
            best_speaker = None
            max_overlap = 0

            for spk in speaker_segments:
                overlap = min(stt["end"], spk["end"]) - max(stt["start"], spk["start"])

                if overlap > 0 and overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = spk["speaker"]

            if best_speaker:
                if best_speaker not in speaker_map:
                    speaker_map[best_speaker] = f"Speaker {speaker_count}"
                    speaker_count += 1

                transcript.append({
                    "speaker": speaker_map[best_speaker],
                    "text": stt["text"]
                })

        return transcript

    # Merge consecutive same-speaker line
    def merge_consecutive(self, transcript):
        if not transcript:
            return []

        merged = [transcript[0]]

        for entry in transcript[1:]:
            if entry["speaker"] == merged[-1]["speaker"]:
                merged[-1]["text"] += " " + entry["text"]
            else:
                merged.append(entry)

        return merged

    # Save RTTM for DER evaluation
    def save_rttm(self, speaker_segments, output_path, file_id):
        with open(output_path, "w") as f:
            for seg in speaker_segments:
                duration = seg["end"] - seg["start"]
                f.write(
                    f"SPEAKER {file_id} 1 {seg['start']:.3f} {duration:.3f} "
                    f"<NA> <NA> {seg['speaker']} <NA> <NA>\n"
                )

    # Full process pipeline
    def process(self, audio_path, output_path):
        stt = self.transcribe(audio_path)
        speakers = self.diarize(audio_path)
        matched = self.match_speakers(stt, speakers)
        merged = self.merge_consecutive(matched)

        # Extract filename (without extension) for RTTM file ID
        file_id = os.path.splitext(os.path.basename(audio_path))[0]

        os.makedirs("results", exist_ok=True)
        self.save_rttm(speakers, "results/system.rttm", file_id=file_id)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for entry in merged:
                f.write(f"[{entry['speaker']}]: {entry['text']}\n")

        print(f"\nDiarized transcript saved to {output_path}")
        return merged
