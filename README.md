# 🚀 Live Meeting Summarizer Application  

An AI-powered web application that converts meeting audio into structured summaries with speaker identification and actionable insights.  

---

## 🌐 Live Demo  
👉 https://live-meeting-summarizer-application.vercel.app  

---

## 📌 Features  

- 🎤 Real-time Speech-to-Text (Whisper)  
- 🧑‍🤝‍🧑 Speaker Diarization (Pyannote)  
- 🧠 AI-based Summarization (LLaMA 3 via Groq API)  
- 📄 Structured summaries with key decisions & action items  
- 💾 Save, download, and manage meeting history  

---

## ⚙️ Tech Stack  

**Frontend:** React.js, Vite, CSS  
**Backend:** Python, FastAPI  
**Database:** MongoDB Atlas  

### AI Models  
- Whisper (Speech-to-Text)  
- Pyannote (Diarization)  
- LLaMA 3 (Summarization via Groq API)  

### Deployment  
- Vercel (Frontend)  
- Hugging Face Spaces (Backend)  

---

## 🔄 Workflow  

1. User records/uploads audio  
2. Audio sent to backend  
3. Whisper → converts speech to text  
4. Pyannote → identifies speakers  
5. LLM → generates summary + action items  
6. Data stored in MongoDB  
7. Results displayed on dashboard  

---

## 📊 Impact  

- Saves time by eliminating manual note-taking  
- Improves accountability with speaker tracking  
- Makes meetings searchable and structured  

---

## 👩‍💻 Author  

Aashika Arunkumar  
