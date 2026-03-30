# MeetMind AI

MeetMind AI is an AI-powered meeting assistant that can:

- Capture live microphone audio (local environments with PyAudio)
- Upload meeting audio/video files
- Transcribe speech to text
- Perform speaker diarization (who spoke when)
- Generate concise meeting summaries
- Export summaries to MD, PDF, and DOCX

The project is split into two apps:

- backend: Flask API for audio processing, diarization, summarization, and exports
- frontend: React + Vite UI for recording, upload, diarization review, and summary views

## Project Structure

- backend
  - app.py
  - requirements.txt
  - .python-version
  - meetmind_ai/
    - api/server.py
    - core/
    - config/settings.py
    - evaluation/
- frontend
  - package.json
  - vite.config.ts
  - src/

## Tech Stack

Backend:

- Flask
- flask-cors
- faster-whisper
- pyannote.audio
- Groq API
- pydub
- python-docx
- reportlab

Frontend:

- React
- Vite
- TypeScript
- Tailwind CSS
- Framer Motion

## Prerequisites

- Python 3.11.x (pinned for deploy compatibility in backend/.python-version)
- Node.js 18+ and npm
- FFmpeg installed and available in PATH (required by pydub for media conversion)

Optional for local live recording:

- PyAudio support on your OS

## Environment Variables

### Backend env (backend/.env)

Required:

- HUGGINGFACE_TOKEN
- GROQ_API_KEY

Recommended:

- CORS_ALLOWED_ORIGINS
  - Example: http://localhost:8080,http://127.0.0.1:8080

Optional tuning:

- WHISPER_MODEL_SIZE (default: base)
- WHISPER_DEVICE (default: cpu)
- WHISPER_COMPUTE_TYPE (default: int8)
- AUDIO_SAMPLE_RATE (default: 16000)
- AUDIO_CHANNELS (default: 1)
- AUDIO_CHUNK_SIZE (default: 1024)
- OUTPUTS_DIR (default: outputs)
- TEMP_DIR (default: temp)

Compatibility note:

- The backend also accepts ALLOWED_ORIGINS as a fallback if CORS_ALLOWED_ORIGINS is not set.

### Frontend env (frontend/.env)

- VITE_API_URL
  - Example: http://localhost:5000

The frontend API layer resolves base URL in this order:

1. VITE_API_BASE_URL
2. VITE_API_URL + /api
3. /api

## Local Development

### 1) Start backend

From the backend folder:

1. Create and activate virtual environment
2. Install dependencies
3. Run API server

Commands:

- Windows PowerShell:
  - py -3.11 -m venv .venv
  - .\.venv\Scripts\Activate.ps1
  - pip install -r requirements.txt
  - py app.py

Backend runs on: http://127.0.0.1:5000

### 2) Start frontend

From the frontend folder:

- npm install
- npm run dev

Frontend runs on: http://127.0.0.1:8080

Vite proxies /api requests to VITE_API_URL in development.

## API Overview

Base URL: /api

Common routes:

- POST /api/start-recording
- POST /api/stop-recording
- GET /api/live-transcript
- POST /api/upload
- POST /api/diarize
- POST /api/wav-to-conversation
- POST /api/summarize
- POST /api/run-pipeline
- GET /api/export?format=md|pdf|docx
- POST /api/evaluate

Health route:

- GET /

## Deployment Notes (Render)

If deploying backend to Render:

- Root directory: backend
- Build command: pip install -r requirements.txt
- Start command: python app.py
- Python version: controlled by backend/.python-version (3.11.11)

Important:

- Python 3.14 may fail with torch version constraints used by this project.
- PyAudio is Windows-only in requirements, so Linux deploys can build successfully.

If deploying frontend separately:

- Set VITE_API_URL to your backend public URL (without /api)

## Outputs

Generated artifacts are stored in backend/outputs, including:

- conversation_*.txt
- diarization_*.json
- exported summary files

## Troubleshooting

- Build fails on torch version:
  - Ensure Python 3.11 is used in backend deploy.
- Live recording does not work on server:
  - Live mic capture is intended for local environments with audio hardware and PyAudio.
- Upload conversion fails:
  - Verify FFmpeg is installed and available in PATH.
- Diarization or summary is empty:
  - Check HUGGINGFACE_TOKEN and GROQ_API_KEY in backend/.env.

## License

Add your preferred license here.
