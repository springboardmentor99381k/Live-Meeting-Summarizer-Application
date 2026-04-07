# 🎤 Live Meeting Summarizer

## Overview
This project is a real-time meeting summarizer that captures audio, converts speech to text, identifies different speakers, and generates structured summaries using pre-trained AI models.

---

## Features
- 🎤 Real-time speech-to-text using Whisper
- 🧑‍🤝‍🧑 Speaker diarization using pyannote.audio
- 🧠 Text summarization using BART transformer model
- 🌐 Interactive Streamlit UI
- 📂 Audio upload support
- 📄 Export summaries as PDF and Markdown
- 📧 Email summary functionality
- 🧾 Structured logging of meeting sessions

---

## Tech Stack
- Python
- Whisper (Speech-to-Text)
- pyannote.audio (Diarization)
- Hugging Face Transformers (BART)
- Streamlit (Frontend UI)

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py