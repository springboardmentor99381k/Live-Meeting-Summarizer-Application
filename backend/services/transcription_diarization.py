import torch
import whisper
import torchaudio
from pyannote.audio import Pipeline

import os
from dotenv import load_dotenv
load_dotenv()


#Diarization
DIARIZATION_TOKEN = os.getenv("HF_TOKEN")

diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=DIARIZATION_TOKEN
)

diarization_pipeline.to(torch.device("cpu"))

# Whisper
whisper_model = whisper.load_model("base")

def process_speech(audio_file: str):
    waveform,sample_rate = torchaudio.load(audio_file)

    diarization= diarization_pipeline({
        "waveform": waveform,
        "sample_rate": sample_rate
    })
    result = whisper_model.transcribe(audio_file)
    segments = result["segments"]

    final_output = []

    speaker_map = {
        "SPEAKER_00": "Speaker 1",
        "SPEAKER_01": "Speaker 2",
        "SPEAKER_02": "Speaker 3",
        "SPEAKER_03": "Speaker 4",
        "SPEAKER_04": "Speaker 5",
        "SPEAKER_05": "Speaker 6",
    }

    for segment in segments:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        speaker = "Unknown"

        # for turn, _, spk in diarization.itertracks(yield_label = True):
        #     if turn.start <= start <= turn.end:
        #         speaker = spk
        #         break
        for turn, _, spk in diarization.itertracks(yield_label=True):
            overlap = min(turn.end, end) - max(turn.start, start)
            if overlap > 0:
               
                speaker = speaker_map.get(spk, spk)
                break

        final_output.append(f"{speaker}: {text}")
    full_transcription = "\n".join(final_output)

    return{
        "lines": final_output,
        "full_text": full_transcription
    }