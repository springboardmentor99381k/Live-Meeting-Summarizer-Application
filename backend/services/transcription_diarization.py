import torch
import whisper
import torchaudio
from pyannote.audio import Pipeline
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

# Diarization
DIARIZATION_TOKEN = os.getenv("HF_TOKEN")
diarization_pipeline = None

try:
    if DIARIZATION_TOKEN and DIARIZATION_TOKEN.startswith("hf_"):
        print("\n[INFO] Loading Pyannote Diarization Pipeline...")
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=DIARIZATION_TOKEN
        )
        if diarization_pipeline:
            diarization_pipeline.to(torch.device("cpu"))
            print("[INFO] Pyannote loaded successfully on CPU.")
    else:
        print("\n[WARNING] Valid HF_TOKEN missing. Speaker diarization will be disabled.\n")
except Exception as e:
    print(f"\n[WARNING] Pyannote failed to load. Diarization disabled. Error: {e}\n")


# Whisper
print("[INFO] Loading Whisper tiny model for maximum speed...")
whisper_model = whisper.load_model("tiny")
print("[INFO] Whisper loaded successfully.")

def process_speech(audio_file: str):
    # Convert WebM to WAV natively using FFmpeg so Torchaudio doesn't crash on Windows
    wav_audio_file = audio_file + ".wav"
    try:
        print("[DEBUG] Converting audio to WAV format for torchaudio compatibility...")
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_file, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_audio_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception as e:
        print(f"[ERROR] FFmpeg conversion failed: {e}")
        wav_audio_file = audio_file  # fallback strictly to original file

    diarization = None
    if diarization_pipeline:
        try:
            print("[DEBUG] Started Pyannote Diarization (This can take 1-3 minutes on CPU)...")
            waveform, sample_rate = torchaudio.load(wav_audio_file)
            diarization = diarization_pipeline({
                "waveform": waveform,
                "sample_rate": sample_rate
            })
            print("[DEBUG] Finished Pyannote Diarization.")
        except Exception as e:
            print(f"[ERROR] Diarization skipped (Load/Processing issue): {e}")

    print("[DEBUG] Started Whisper transcription (This can take 10-30 seconds)...")
    result = whisper_model.transcribe(wav_audio_file)
    print("[DEBUG] Finished Whisper transcription.")
    segments = result["segments"]

    final_output = []
    speaker_map = {
        f"SPEAKER_{i:02d}": f"Speaker {i+1}" for i in range(10)
    }

    for segment in segments:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        speaker = "Speaker"

        if diarization:
            for turn, _, spk in diarization.itertracks(yield_label=True):
                overlap = min(turn.end, end) - max(turn.start, start)
                if overlap > 0:
                    speaker = speaker_map.get(spk, spk)
                    break

        final_output.append(f"{speaker}: {text}")

    full_transcription = "\n".join(final_output)

    # Cleanup temp wav file
    if os.path.exists(wav_audio_file) and wav_audio_file != audio_file:
        os.remove(wav_audio_file)

    return {
        "lines": final_output,
        "full_text": full_transcription
    }