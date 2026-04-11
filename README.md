# AI Live Meeting Summarizer

A full-stack application that provides real-time speech-to-text transcription, speaker diarization, and meeting summarization using AI.

## Architecture
- **Frontend**: React, Vite, TailwindCSS
- **Backend**: FastAPI, PyTorch, Whisper, Pyannote for speaker diarization, Transformers for summarization

## Setup

1. **Backend Configuration**
   Change to the `backend/` directory, create a `.env` file with the following variables:
   - `HF_TOKEN`: Your Hugging Face user access token (Required for Pyannote speaker diarization)
   - `GEMINI_TOKEN`: Gemini API key (if applicable)
   - `EMAIL` & `EMAIL_PASSWORD`: For the email sending feature

2. **Run Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Run Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Note on Hugging Face token
You must accept the user conditions on the Hugging Face hub for `pyannote/speaker-diarization-3.1` and `pyannote/segmentation-3.0` models to use this project out of the box.
