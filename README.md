# Live-Meeting-Summarizer-Application

live working link
# https://shreya1811-live-meeting-summarizer.hf.space

Project Development Phases
### Week 1 – Project Setup & Speech-to-Text Evaluation**
Designed the overall system pipeline: Audio → Text → Speaker Identification → Summary.
Studied and compared Speech-to-Text (STT) models such as Whisper and Vosk.
Collected meeting audio samples from the AMI Meeting Corpus and custom recordings.
Evaluated transcription accuracy using Word Error Rate (WER).\
**Output**\
System architecture design.
Sample meeting audio dataset.
STT model comparison report.\
**Tech Stack**
Python, Vosk, OpenAI Whisper, JiWER (for WER calculation)\

### Week 2 – Real-Time Speech-to-Text
Implemented live audio capture from the microphone.
Built a real-time speech-to-text transcription system.
Displayed live transcription output in the terminal.
Optimized speed and transcription accuracy.\
**Output**
Working real-time STT application.
Transcription logs.
Accuracy report (WER < 15%).
**Tech Stack**\
Python, PyAudio / SoundDevice, Threading, Selected STT model (Whisper / Vosk)\

### Week 3 – Speaker Diarization
Implemented speaker identification in meeting audio.
Detected and labeled multiple speakers in conversations.
Integrated diarization output with transcription results to generate speaker-wise transcripts.\
**Output**\
Speaker-wise meeting transcript.
Diarization module.
Accuracy report (DER < 20%).\
**Tech Stack**\
pyannote.audio, torchaudio, AMI Meeting Corpus dataset\

### Week 4 - AI-based summarization

Implemented AI-powered summarization for meeting transcripts.
Generated structured summaries from speaker-wise meeting transcripts.
Designed prompt templates to extract important information such as key points, decisions, and action items.
Integrated the summarization module with diarized transcripts for automated meeting insights.\

**Output**\
Structured meeting summary.
Prompt templates for summarization.
Sample summarized meeting outputs.

**Tech Stack**\
LLaMA 3.1 (Groq API), ROUGE evaluation metric

### Week 5 - Backend Integration

Connected Speech-to-Text, Speaker Diarization, and Summarization into a unified pipeline.
Implemented multi-threaded audio capture to ensure continuous recording without UI freezing.
Developed logic to trigger diarization and summarization sequences only after the recording session stops.
Handled background tasks and process synchronization to prevent overlapping resource execution and system crashes.

**Output**\
Complete backend processing pipeline
End-to-end functional demo (Audio → Transcript → Summary)
Thread-safe execution environment

**Tech Stack**\
Python (threading, queue, asyncio), Whisper, Pyannote.audio

### Week 6 - Streamlit UI Development

Designed a real-time interactive frontend for the AI Meeting Summarizer.
Developed a responsive interface featuring Start/Stop controls and dynamic status indicators.
Implemented live Speech-to-Text (STT) updates on the UI during active recording sessions.
Created dedicated viewing components for diarized transcripts and final AI-generated summaries.

**Output**\
Fully functional Streamlit web application.
Real-time transcription log and summary viewer.
Interactive status bar (Recording/Transcribing/Summarizing).

**Tech Stack**\
Streamlit, , Python, CSS Custom Styling

### Week 7

Added download feature.
Final overall testing. 

### Week 8

Created the documemntation.
