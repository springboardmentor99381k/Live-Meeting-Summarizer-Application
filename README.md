# Live-Meeting-Summarizer-Application

# AI Live Meeting Summarizer

AI Live Meeting Summarizer is a system that records meetings, converts speech to text, identifies different speakers, and generates speaker-wise transcripts.  
This project is being developed in stages to build a complete AI meeting analysis pipeline.

Currently implemented: **Week 1 – Week 3**

---

# Features

## Week 1 – Audio Recording
- Record meeting audio from microphone
- Save recording as `.wav` file
- Basic audio handling pipeline

## Week 2 – Speech-to-Text
- Convert recorded audio to text
- Implemented using Whisper speech recognition model
- Produces timestamped transcription segments

## Week 3 – Speaker Diarization
- Detect different speakers in the meeting audio
- Assign speaker labels to audio segments
- Merge diarization output with speech-to-text results
- Generate a **speaker-wise transcript**

Example Output:

Speaker 1: Well, it's the kickoff meeting for our project.  
Speaker 2: I'm David and I'm the industrial designer.

---

# Models Used

Speech Recognition  
- Whisper (OpenAI)

Speaker Diarization  
- pyannote speaker diarization pipeline

Dataset Used for Testing  
- AMI Meeting Corpus

---

# Installation

Clone the repository
git clone <repository-link>
cd AI_Live_Meeting_Summarizer

Create a virtual environment
python -m venv week3_env


Activate the environment

Windows
week3_env\Scripts\activate


Install dependencies
pip install -r requirements.txt


---

# Running the Pipeline

Navigate to the diarization folder
cd week3_diarization
python main.py



Pipeline execution steps:

1. Transcribe audio using Whisper
2. Perform speaker diarization
3. Merge speaker segments with transcription
4. Generate speaker-wise transcript

---

# Diarization Performance

The system uses the pretrained pyannote speaker diarization model.  
According to benchmark evaluations on the AMI Meeting Corpus, this model achieves approximately **10–18% Diarization Error Rate (DER)** under standard meeting conditions.

---

# Future Work

Planned improvements for upcoming stages:

- Automatic meeting summarization
- Action item extraction
- Key point detection
- Real-time meeting processing
- Web interface for uploading meetings

---

# Author

AI Live Meeting Summarizer Project  
Implementation completed up to Week 3

