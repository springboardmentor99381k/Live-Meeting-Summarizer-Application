# Live Meeting Summarizer Application

A Python-based backend pipeline for recording live meetings, transcribing audio, detecting speakers, and generating summaries.

## Features

- Real-time audio recording using threading and queues
- Speech-to-text transcription with OpenAI Whisper
- Speaker diarization with pyannote.audio
- Meeting summarization using Hugging Face transformers
- Modular and production-ready code

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Hugging Face token for pyannote (if required)

## Usage

Run `python main.py` to start a demo recording (10 seconds), process, and generate outputs.

## Project Structure

- `backend/`: Core modules
  - `audio_capture.py`: Audio recording functionality
  - `transcription.py`: Speech-to-text
  - `diarization.py`: Speaker detection
  - `summarizer.py`: Summary generation
  - `pipeline.py`: Orchestrates the processing
- `outputs/`: Generated files (transcript.txt, speakers.txt, summary.txt)
- `main.py`: Entry point
- `requirements.txt`: Dependencies

## Output Format

The summary follows the specified format with Key Points, Action Items, and Short Summary.