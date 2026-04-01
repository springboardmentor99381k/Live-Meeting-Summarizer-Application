"""
Meeting Summarizer — Streamlit UI  (Week 6)
- Real-time live STT chunks shown while recording
- Start / Stop buttons with animated waveform
- Status bar: Recording → Transcribing → Diarizing → Summarizing → Done
- Diarized transcript + summary shown after processing
- Full file-upload mode
- Backend: cached Whisper + pyannote (load once per session)
"""

import os, sys, time, queue, threading, wave, datetime, tempfile, logging, html
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
logging.getLogger("streamlit").setLevel(logging.ERROR)
from streamlit.runtime.scriptrunner import add_script_run_ctx

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS (keep original design exactly) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0D0E12 !important;
    color: #E8E6E1 !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] > .main { background-color: #0D0E12 !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem !important; max-width: 1300px !important; }

/* Masthead */
.ms-head { border-bottom: 1px solid #1E2028; padding-bottom: 1.4rem; margin-bottom: 1.6rem; }
.ms-head h1 { font-family: 'DM Serif Display', serif; font-size: 2.4rem; font-weight: 400;
    color: #F0EDE8; margin: 0; letter-spacing: -0.02em; }
.ms-head .sub { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #5A5E6B;
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.3rem; }

/* Status badge */
.ms-badge { display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.35rem 0.9rem; border-radius: 2px; font-family: 'DM Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 1.6rem; border: 1px solid transparent; }
.badge-idle       { background:#12141A; border-color:#1E2028; color:#5A5E6B; }
.badge-recording  { background:#1A0A0A; border-color:#4A1A1A; color:#E05A5A; }
.badge-processing { background:#0A1218; border-color:#1A3040; color:#5A9ABF; }
.badge-done       { background:#091510; border-color:#183020; color:#4AB87A; }
.ms-dot { width:6px; height:6px; border-radius:50%; display:inline-block; }
.badge-recording  .ms-dot { background:#E05A5A; animation:blink 1s infinite; }
.badge-processing .ms-dot { background:#5A9ABF; animation:blink 1.2s infinite; }
.badge-done       .ms-dot { background:#4AB87A; }
.badge-idle       .ms-dot { background:#3A3E4A; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* Panel */
.ms-panel { background:#12141A; border:1px solid #1E2028; border-radius:4px;
    padding:1.6rem 1.8rem; margin-bottom:1.4rem; }
.ms-panel-title { font-family:'DM Mono',monospace; font-size:0.66rem;
    letter-spacing:0.1em; text-transform:uppercase; color:#3A3E4A;
    margin-bottom:1.1rem; display:flex; align-items:center; gap:0.5rem; }
.ms-panel-title::after { content:''; flex:1; height:1px; background:#1E2028; }

/* Buttons */
div.stButton > button {
    font-family:'DM Mono',monospace !important; font-size:0.74rem !important;
    letter-spacing:0.06em !important; text-transform:uppercase !important;
    border-radius:2px !important; border:1px solid #2A2E38 !important;
    background:#1A1C24 !important; color:#C8C5C0 !important;
    padding:0.55rem 1.2rem !important; height:auto !important; width:100%;
    transition:all 0.15s !important; }
div.stButton > button:hover { background:#22242E !important;
    border-color:#3A3E4A !important; color:#F0EDE8 !important; }
div.stButton > button:focus { box-shadow:none !important; outline:none !important; }

/* Live transcript + diarized transcript box */
.ms-transcript { background:#0A0B0E; border:1px solid #1A1C22; border-radius:3px;
    padding:1.1rem 1.3rem; min-height:200px; max-height:380px; overflow-y:auto;
    font-family:'DM Mono',monospace; font-size:0.8rem; line-height:1.75; color:#9A9DAA; }
.spk  { color:#5A9ABF; font-weight:500; display:block; margin-top:0.5rem; }
.line { color:#C8C5C0; padding-left:0.9rem; display:block; }
.dim  { color:#2A2E38; font-style:italic; }
.live { color:#6A9A7A; font-style:italic; }

/* Summary box */
.ms-summary { background:#0A0B0E; border:1px solid #1A1C22; border-radius:3px;
    padding:1.3rem 1.5rem; font-size:0.88rem; line-height:1.8; color:#C8C5C0;
    white-space:pre-wrap; min-height:120px; }

/* Metric */
.ms-metric { background:#0A0B0E; border:1px solid #1E2028; border-radius:3px;
    padding:0.9rem 1rem; text-align:center; }
.ms-metric .val { font-family:'DM Serif Display',serif; font-size:1.7rem;
    color:#E8E6E1; display:block; line-height:1.2; }
.ms-metric .lbl { font-family:'DM Mono',monospace; font-size:0.62rem;
    letter-spacing:0.08em; text-transform:uppercase; color:#3A3E4A;
    margin-top:0.25rem; display:block; }

/* Step progress bar */
.ms-step { padding:1rem 1.3rem; background:#0A0C14; border:1px solid #1A2A3A;
    border-radius:3px; margin-bottom:1rem; }
.ms-step .step-label { font-family:'DM Mono',monospace; font-size:0.82rem;
    color:#C8C5C0; margin-bottom:0.6rem; }
.ms-step .step-num { font-family:'DM Mono',monospace; font-size:0.65rem;
    color:#5A9ABF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.4rem; }
.ms-bar-bg  { height:2px; background:#1A2030; border-radius:1px; }
.ms-bar-fill{ height:100%; background:#5A9ABF; border-radius:1px; }

/* Waveform animation */
.ms-wave { display:flex; align-items:center; gap:3px; height:28px; margin:0.8rem 0; }
.ms-wave span { display:inline-block; width:3px; background:#E05A5A;
    border-radius:2px; animation:wavebar 0.8s ease-in-out infinite; }
.ms-wave span:nth-child(1){animation-delay:0.0s}
.ms-wave span:nth-child(2){animation-delay:0.1s}
.ms-wave span:nth-child(3){animation-delay:0.2s}
.ms-wave span:nth-child(4){animation-delay:0.3s}
.ms-wave span:nth-child(5){animation-delay:0.4s}
.ms-wave span:nth-child(6){animation-delay:0.3s}
.ms-wave span:nth-child(7){animation-delay:0.2s}
.ms-wave span:nth-child(8){animation-delay:0.1s}
@keyframes wavebar { 0%,100%{height:4px} 50%{height:22px} }

/* File uploader */
[data-testid="stFileUploader"] section {
    background:#0A0B0E !important; border:1px dashed #2A2E38 !important; border-radius:3px !important; }
[data-testid="stFileUploaderDropzoneInstructions"] div span {
    color:#5A5E6B !important; font-family:'DM Mono',monospace !important; font-size:0.8rem !important; }

/* Inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input {
    background:#0A0B0E !important; border-color:#1E2028 !important;
    color:#C8C5C0 !important; font-family:'DM Mono',monospace !important;
    font-size:0.8rem !important; border-radius:2px !important; }
label { color:#5A5E6B !important; font-family:'DM Mono',monospace !important;
    font-size:0.72rem !important; letter-spacing:0.06em !important; text-transform:uppercase !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    font-family:'DM Mono',monospace !important; font-size:0.7rem !important;
    letter-spacing:0.06em !important; text-transform:uppercase !important;
    border-radius:2px !important; border:1px solid #2A2E38 !important;
    background:#12141A !important; color:#9A9DAA !important;
    padding:0.45rem 1rem !important; width:100%; }
[data-testid="stDownloadButton"] > button:hover {
    background:#1A1C24 !important; color:#E8E6E1 !important; }

hr { border-color:#1E2028 !important; margin:1rem 0 !important; }
[data-testid="stAlert"] { background:#12141A !important; border-color:#1E2028 !important;
    border-radius:2px !important; font-family:'DM Mono',monospace !important; font-size:0.78rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Backend path ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

sys.path.insert(0, SRC_DIR)


# ── Cached model loaders (load ONCE per session) ──────────────────────────────
@st.cache_resource(show_spinner=False)
def _load_whisper(model_size: str):
    import whisper
    return whisper.load_model(model_size)

@st.cache_resource(show_spinner=False)
def _load_pyannote(hf_token: str):
    import torch
    from pyannote.audio import Pipeline as PA
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return PA.from_pretrained("pyannote/speaker-diarization-3.1", token=hf_token).to(device)


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "mode":               "record",
        "status":             "idle",
        "whisper_model":      "tiny",
        "language":           "en",
        "raw_transcript":     "",
        "diarized_transcript":"",
        "summary":            "",
        "detected_speakers":  0,
        "live_text":          "",       # ← real-time STT chunks
        "error":              None,
        "is_recording":       False,
        "rec_start":          0.0,
        "rec_duration":       0.0,
        "audio_path":         None,
        "pipeline_result":    None,
        "pipeline_error":     None,
        "pipeline_running":   False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

if "rec_frames"    not in st.session_state: st.session_state["rec_frames"]    = []
if "rec_stop_ev"   not in st.session_state: st.session_state["rec_stop_ev"]   = None
if "rec_stream"    not in st.session_state: st.session_state["rec_stream"]    = None
if "live_q"        not in st.session_state: st.session_state["live_q"]        = None
if "pipeline_q"    not in st.session_state: st.session_state["pipeline_q"]    = queue.Queue()


# ── Real-time STT thread ──────────────────────────────────────────────────────
SAMPLE_RATE  = 16000
CHUNK_SEC    = 3       # transcribe a chunk every N seconds
MIN_LIVE_CHUNK_SECONDS = 1.5
MIN_RECORD_SECONDS = 1.0
MIN_AUDIO_SAMPLES = int(SAMPLE_RATE * MIN_RECORD_SECONDS)
MIN_LIVE_CHUNK_SAMPLES = int(SAMPLE_RATE * MIN_LIVE_CHUNK_SECONDS)
MIN_DIARIZATION_SECONDS = 1.0
DEFAULT_FALLBACK_SPEAKERS = 2

def _append_live_text(existing: str, new_text: str) -> str:
    new_text = " ".join(str(new_text).split()).strip()
    if not new_text:
        return existing
    if not existing:
        return new_text
    separator = "" if existing.endswith(("-", "/", "(")) else " "
    return f"{existing.rstrip()}{separator}{new_text}".strip()


def _drain_live_queue() -> None:
    lq = st.session_state.get("live_q")
    if not lq:
        return

    while not lq.empty():
        try:
            txt = lq.get_nowait()
            st.session_state["live_text"] = _append_live_text(
                st.session_state.get("live_text", ""),
                txt,
            )
        except queue.Empty:
            break


def _live_stt_thread(stop_ev, frame_list, live_q, model_size, language):
    """Runs alongside recording. Every CHUNK_SEC seconds, transcribes buffer."""
    live_model_size = "tiny" if model_size != "tiny" else model_size
    model = _load_whisper(live_model_size)
    last_idx = 0
    while True:
        should_stop = stop_ev.wait(CHUNK_SEC)
        current = list(frame_list)          # snapshot
        new = current[last_idx:]
        if new:
            try:
                chunk = np.concatenate(new, axis=0).flatten().astype(np.float32) / 32768.0
                enough_audio = chunk.size >= MIN_LIVE_CHUNK_SAMPLES
                if enough_audio or should_stop:
                    last_idx = len(current)
                    result = model.transcribe(
                        chunk,
                        language=language,
                        fp16=False,
                        word_timestamps=False,
                        condition_on_previous_text=False,
                        verbose=False,
                    )
                    txt = result["text"].strip()
                    if txt:
                        live_q.put(txt)
            except Exception:
                pass
        if should_stop:
            break


# ── Recording helpers ─────────────────────────────────────────────────────────
def _start_recording():
    try:
        import sounddevice as sd
        frames  = []
        stop_ev = threading.Event()
        live_q  = queue.Queue()

        def _cb(indata, n, t, status):
            if not stop_ev.is_set():
                frames.append(indata.copy())

        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                                dtype="int16", callback=_cb)
        stream.start()

        # Start live STT in background
        t = threading.Thread(
            target=_live_stt_thread,
            args=(stop_ev, frames, live_q,
                  st.session_state["whisper_model"],
                  st.session_state["language"]),
            daemon=True,
        )
        add_script_run_ctx(t)
        t.start()

        st.session_state.update({
            "rec_frames":   frames,
            "rec_stop_ev":  stop_ev,
            "rec_stream":   stream,
            "live_q":       live_q,
            "is_recording": True,
            "rec_start":    time.time(),
            "status":       "recording",
            "live_text":    "",
            "error":        None,
        })
    except Exception as e:
        st.session_state["error"] = f"Microphone error: {e}"


def _stop_recording():
    try:
        stop_ev = st.session_state["rec_stop_ev"]
        stream  = st.session_state["rec_stream"]
        frames  = st.session_state["rec_frames"]

        if stop_ev: stop_ev.set()
        if stream:
            stream.stop()
            stream.close()

        # Drain any remaining live STT chunks, including the final short chunk.
        _drain_live_queue()

        dur = time.time() - st.session_state["rec_start"]
        st.session_state["rec_duration"] = dur
        st.session_state["is_recording"] = False

        if not frames:
            st.session_state["error"]  = "No audio captured. Check your microphone."
            st.session_state["status"] = "idle"
            return

        audio_data = np.concatenate(frames, axis=0)
        sample_count = int(audio_data.shape[0]) if audio_data.ndim > 0 else 0
        if sample_count < MIN_AUDIO_SAMPLES:
            st.session_state["error"] = (
                f"Recording is too short. Please record at least {MIN_RECORD_SECONDS:.0f} second."
            )
            st.session_state["status"] = "idle"
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(AUDIO_DIR, exist_ok=True)
        wav_path = os.path.join(AUDIO_DIR, f"recording_{ts}.wav")
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE); wf.writeframes(audio_data.tobytes())

        _start_pipeline(wav_path)

    except Exception as e:
        st.session_state["error"]        = f"Stop error: {e}"
        st.session_state["is_recording"] = False
        st.session_state["status"]       = "idle"


# ── Pipeline (background thread) ──────────────────────────────────────────────
def _prepare_audio(audio_path: str) -> str:
    """Convert audio once to mono 16 kHz WAV for faster downstream processing."""
    import soundfile as sf

    data, sr = sf.read(audio_path, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = np.asarray(data, dtype=np.float32).reshape(-1)
    if data.size == 0:
        raise ValueError("Audio file is empty. Please record again.")
    if sr != 16000:
        new_len = int(len(data) * 16000 / sr)
        if new_len <= 0:
            raise ValueError("Audio file is too short to process. Please record again.")
        data = np.interp(
            np.linspace(0, len(data) - 1, new_len),
            np.arange(len(data)),
            data,
        ).astype(np.float32)
        sr = 16000

    os.makedirs(AUDIO_DIR, exist_ok=True)
    prepared_path = os.path.join(
        AUDIO_DIR,
        f"prepared_{Path(audio_path).stem}_{int(time.time())}.wav",
    )
    sf.write(prepared_path, data, sr)
    return prepared_path


def _get_audio_duration_seconds(audio_path: str) -> float:
    import soundfile as sf

    info = sf.info(audio_path)
    if info.samplerate <= 0:
        return 0.0
    return float(info.frames) / float(info.samplerate)


def _validate_audio_duration(duration_seconds: float) -> None:
    if duration_seconds < MIN_RECORD_SECONDS:
        raise ValueError(
            f"Recording is too short. Please record at least {MIN_RECORD_SECONDS:.0f} second."
        )


def _simple_speaker_split(whisper_result: dict, num_speakers: int) -> list[dict]:
    """Fast fallback: split transcript segments evenly across speakers."""
    segments = whisper_result.get("segments", [])
    if not segments:
        return []

    max_speakers = max(1, num_speakers)
    mapped: list[dict] = []
    for index, segment in enumerate(segments):
        speaker_num = min((index % max_speakers) + 1, max_speakers)
        mapped.append(
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "speaker": f"Speaker {speaker_num}",
            }
        )
    return mapped


def _has_usable_speech(whisper_result: dict, audio_data: np.ndarray) -> bool:
    segments = whisper_result.get("segments", [])
    text = str(whisper_result.get("text", "")).strip()
    if not segments or not text:
        return False
    if audio_data.size == 0:
        return False

    rms = float(np.sqrt(np.mean(np.square(audio_data, dtype=np.float32))))
    return rms >= 0.003


def _fallback_labelled_transcript(whisper_result: dict, num_speakers: int) -> str:
    from pipeline import align

    mapped = _simple_speaker_split(whisper_result, num_speakers)
    if mapped:
        return align(whisper_result, mapped)

    raw_text = str(whisper_result.get("text", "")).strip()
    return raw_text or "No speech detected."


def _count_speakers_in_transcript(transcript: str) -> int:
    speakers = {
        line[:-1].strip()
        for line in transcript.splitlines()
        if line.strip().endswith(":") and not line.startswith("  ")
    }
    return len(speakers)


def _normalize_speaker_turns(diarization) -> list[dict]:
    """Convert pyannote diarization output into align()-friendly speaker turns."""
    speaker_names: dict[str, str] = {}
    speaker_index = 1
    turns: list[dict] = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_key = str(speaker)
        if speaker_key not in speaker_names:
            speaker_names[speaker_key] = f"Speaker {speaker_index}"
            speaker_index += 1

        turns.append(
            {
                "start": float(turn.start),
                "end": float(turn.end),
                "speaker": speaker_names[speaker_key],
            }
        )

    turns.sort(key=lambda item: (item["start"], item["end"]))
    return turns


def _run_pyannote_diarization(audio_path: str, hf_token: str) -> list[dict]:
    diarizer = _load_pyannote(hf_token)
    diarization = diarizer(audio_path)
    return _normalize_speaker_turns(diarization)


def _run_pipeline(audio_path, whisper_model, language, q):
    """Background thread. Communicates ONLY via queue — never touches st.session_state."""
    try:
        # Suppress all warnings in this thread
        import warnings
        warnings.filterwarnings("ignore")

        import torch, soundfile as sf
        from config import Config
        from pipeline import align, summarize

        config = Config(num_speakers=1,
                        whisper_model=whisper_model,
                        language=language,
                        output_dir=OUTPUT_DIR)
        config.validate()
        raw_duration = _get_audio_duration_seconds(audio_path)
        _validate_audio_duration(raw_duration)
        prepared_audio_path = _prepare_audio(audio_path)
        prepared_duration = _get_audio_duration_seconds(prepared_audio_path)
        _validate_audio_duration(prepared_duration)
        speaker_count = 0

        # 1. Transcribe
        q.put(("status", "transcribing"))
        model  = _load_whisper(whisper_model)
        result = model.transcribe(
            prepared_audio_path,
            word_timestamps=False,
            language=language,
            task="transcribe",
            fp16=False,
            beam_size=1,
            best_of=1,
            temperature=0,
            condition_on_previous_text=False,
            verbose=False,
        )
        raw = result["text"].strip()

        # 2. Diarize — reuse the same prepared 16kHz mono audio
        q.put(("status", "diarizing"))
        try:
            data, sr = sf.read(prepared_audio_path, dtype="float32")
            data = np.asarray(data, dtype=np.float32).reshape(-1)
            if data.size == 0 or not sr:
                raise ValueError("Recorded audio is empty after preprocessing. Please try again.")

            duration_sec = len(data) / sr if sr else 0
            usable_speech = _has_usable_speech(result, data)

            if duration_sec < MIN_DIARIZATION_SECONDS:
                labelled = _fallback_labelled_transcript(result, DEFAULT_FALLBACK_SPEAKERS)
            elif not usable_speech:
                labelled = _fallback_labelled_transcript(result, DEFAULT_FALLBACK_SPEAKERS)
            else:
                speaker_turns = _run_pyannote_diarization(
                    prepared_audio_path,
                    config.hf_token,
                )
                if speaker_turns:
                    labelled = align(result, speaker_turns)
                    speaker_count = len({turn["speaker"] for turn in speaker_turns})
                else:
                    labelled = _fallback_labelled_transcript(result, DEFAULT_FALLBACK_SPEAKERS)
        except Exception:
            labelled = _fallback_labelled_transcript(result, DEFAULT_FALLBACK_SPEAKERS)

        if speaker_count <= 0:
            speaker_count = _count_speakers_in_transcript(labelled)

        # 3. Summarize
        q.put(("status", "summarizing"))
        summary = summarize(labelled, config)

        # 4. Save outputs
        os.makedirs(config.output_dir, exist_ok=True)
        for fn, txt in [("raw_transcript.txt", raw),
                        ("diarized_transcript.txt", labelled),
                        ("meeting_summary.txt", summary)]:
            with open(os.path.join(config.output_dir, fn), "w", encoding="utf-8") as f:
                f.write(txt)
                

        q.put(("done", {
            "raw": raw,
            "diarized": labelled,
            "summary": summary,
            "speaker_count": speaker_count,
        }))

    except Exception as e:
        q.put(("error", str(e)))


def _start_pipeline(audio_path):
    duration = 0.0
    try:
        duration = _get_audio_duration_seconds(audio_path)
    except Exception:
        duration = 0.0

    st.session_state["pipeline_q"] = queue.Queue()
    st.session_state.update({
        "audio_path": audio_path, "pipeline_result": None,
        "pipeline_error": None,   "pipeline_running": True,
        "raw_transcript": "",     "diarized_transcript": "",
        "summary": "",            "error": None,
        "detected_speakers": 0,
        "rec_duration": duration,
        "status": "transcribing",
    })
    t = threading.Thread(
        target=_run_pipeline,
        args=(audio_path, st.session_state["whisper_model"], st.session_state["language"],
              st.session_state["pipeline_q"]),
        daemon=True,
    )
    add_script_run_ctx(t)
    t.start()


def _reset():
    for k, v in {
        "status":"idle","raw_transcript":"","diarized_transcript":"",
        "summary":"","live_text":"","error":None,"audio_path":None,
        "rec_duration":0.0,"is_recording":False,"rec_start":0.0,
        "detected_speakers":0,
        "pipeline_result":None,"pipeline_error":None,"pipeline_running":False,
        "rec_frames":[],"rec_stop_ev":None,"rec_stream":None,"live_q":None,
    }.items():
        st.session_state[k] = v


def _drain_runtime_queues():
    """Apply background-thread updates from the main Streamlit thread."""
    if st.session_state.get("pipeline_running"):
        pipeline_q = st.session_state.get("pipeline_q")
        try:
            while True:
                if pipeline_q is None:
                    break
                msg_type, payload = pipeline_q.get_nowait()
                if msg_type == "status":
                    st.session_state["status"] = payload
                elif msg_type == "done":
                    st.session_state["raw_transcript"]      = payload["raw"]
                    st.session_state["diarized_transcript"] = payload["diarized"]
                    st.session_state["summary"]             = payload["summary"]
                    st.session_state["detected_speakers"]   = payload.get("speaker_count", 0)
                    st.session_state["status"]              = "done"
                    st.session_state["pipeline_running"]    = False
                elif msg_type == "error":
                    st.session_state["error"]            = payload
                    st.session_state["status"]           = "idle"
                    st.session_state["pipeline_running"] = False
        except queue.Empty:
            pass

    if st.session_state["is_recording"]:
        _drain_live_queue()


# ── Status badge ──────────────────────────────────────────────────────────────
STATUS_MAP = {
    "idle":         ("badge-idle",       "Awaiting Input"),
    "recording":    ("badge-recording",  "Recording"),
    "transcribing": ("badge-processing", "Transcribing Audio"),
    "diarizing":    ("badge-processing", "Diarizing Speakers"),
    "summarizing":  ("badge-processing", "Generating Summary"),
    "done":         ("badge-done",       "Complete"),
}

def render_badge():
    cls, label = STATUS_MAP.get(st.session_state["status"], ("badge-idle","Idle"))
    st.markdown(f'<div class="ms-badge {cls}"><span class="ms-dot"></span>{label}</div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# UI RENDER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ms-head">
    <h1>Meeting Summarizer</h1>
    <div class="sub">Whisper · Pyannote · Groq LLM</div>
</div>""", unsafe_allow_html=True)

def _render_main_ui():
    render_badge()

    st.markdown('<div class="ms-panel-title">Input Mode</div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([2, 2, 8])
    with c1:
        if st.button(("▶  " if st.session_state["mode"]=="record" else "")+"Record",
                     key="btn_mode_rec"):
            st.session_state["mode"] = "record"
    with c2:
        if st.button(("▶  " if st.session_state["mode"]=="file" else "")+"Upload",
                     key="btn_mode_file"):
            st.session_state["mode"] = "file"

    st.markdown("<hr>", unsafe_allow_html=True)

    left, right = st.columns([5, 5], gap="large")

    with left:
        st.markdown('<div class="ms-panel"><div class="ms-panel-title">Configuration</div>',
                    unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            models = ["tiny","base","small","medium","large"]
            st.session_state["whisper_model"] = st.selectbox(
                "Whisper", models, index=models.index(st.session_state["whisper_model"]),
                key="cfg_model")
        with cc2:
            langs = ["en","hi","fr","de","es","zh","ar","ja"]
            cur = st.session_state["language"]
            if cur not in langs:
                cur = "en"
            st.session_state["language"] = st.selectbox(
                "Language", langs, index=langs.index(cur), key="cfg_lang")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state["mode"] == "record":
            st.markdown('<div class="ms-panel"><div class="ms-panel-title">Microphone Recording</div>',
                        unsafe_allow_html=True)

            is_rec = st.session_state["is_recording"]
            pipeline_busy = st.session_state["pipeline_running"]

            if not is_rec and not pipeline_busy and st.session_state["status"] in ("idle", "done"):
                if st.button("⬤  Start Recording", key="btn_start"):
                    _start_recording()

            elif is_rec:
                dur = time.time() - st.session_state["rec_start"]
                m, s = int(dur // 60), int(dur % 60)
                st.markdown(f"""
                <div style="text-align:center; padding:1rem 0;">
                    <div class="ms-wave">{'<span></span>'*8}</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.5rem;
                                color:#E05A5A;letter-spacing:0.04em;margin:0.4rem 0;">
                        {m:02d}:{s:02d}
                    </div>
                    <div style="font-family:'DM Mono',monospace;font-size:0.66rem;
                                color:#3A3E4A;text-transform:uppercase;letter-spacing:0.1em;">
                        Recording in progress
                    </div>
                </div>""", unsafe_allow_html=True)

                if st.button("■  Stop & Process", key="btn_stop"):
                    _stop_recording()

                st.markdown('<div class="ms-panel-title" style="margin-top:1rem;">Live Transcription</div>',
                            unsafe_allow_html=True)
                live = st.session_state["live_text"].strip()
                body = (
                    f'<span class="live">{html.escape(live)}</span>'
                    if live else '<span class="dim">Listening… (updates every few seconds)</span>'
                )
                st.markdown(f'<div class="ms-transcript">{body}</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.markdown('<div class="ms-panel"><div class="ms-panel-title">Audio File Upload</div>',
                        unsafe_allow_html=True)

            uploaded = st.file_uploader(
                "WAV / MP3 / M4A / FLAC / OGG",
                type=["wav", "mp3", "m4a", "flac", "ogg"],
                label_visibility="collapsed", key="file_upload")

            if uploaded:
                size_kb = uploaded.size / 1024
                st.markdown(f"""
                <div style="font-family:'DM Mono',monospace;font-size:0.76rem;color:#5A9ABF;
                            padding:0.7rem 1rem;background:#0A0B0E;border:1px solid #1A2A38;
                            border-radius:2px;margin:0.8rem 0;">
                    ✓ &nbsp;{uploaded.name}&nbsp;·&nbsp;{size_kb:.1f} KB
                </div>""", unsafe_allow_html=True)

                if not st.session_state["pipeline_running"] and st.session_state["status"] in ("idle", "done"):
                    if st.button("▶  Process File", key="btn_process"):
                        suffix = Path(uploaded.name).suffix or ".wav"
                        os.makedirs(AUDIO_DIR, exist_ok=True)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=AUDIO_DIR) as tmp:
                            tmp.write(uploaded.read())
                            tmp_path = tmp.name
                        _start_pipeline(tmp_path)

            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state["pipeline_running"] or st.session_state["status"] in (
                "transcribing", "diarizing", "summarizing"):
            step_map = {
                "transcribing": (1, "Running Whisper STT"),
                "diarizing":    (2, "Speaker Diarization"),
                "summarizing":  (3, "Generating Summary via Groq"),
            }
            n, label = step_map.get(st.session_state["status"], (1, "Processing…"))
            pct = int((n / 3) * 100)
            st.markdown(f"""
            <div class="ms-step">
                <div class="step-num">Step {n} of 3</div>
                <div class="step-label">{label}</div>
                <div class="ms-bar-bg"><div class="ms-bar-fill" style="width:{pct}%;"></div></div>
            </div>""", unsafe_allow_html=True)

        if st.session_state["error"]:
            st.error(f"⚠ {st.session_state['error']}")
            if st.button("Dismiss", key="btn_dismiss"):
                st.session_state["error"] = None

        if st.session_state["status"] == "done":
            st.markdown("<div style='margin-bottom:0.8rem;'>", unsafe_allow_html=True)
            if st.button("↺  New Session", key="btn_reset"):
                _reset()
            st.markdown("</div>", unsafe_allow_html=True)

            raw = st.session_state["raw_transcript"]
            words = len(raw.split()) if raw else 0
            dur = st.session_state["rec_duration"]
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="ms-metric"><span class="val">{words}</span>'
                            f'<span class="lbl">Words</span></div>', unsafe_allow_html=True)
            with m2:
                speaker_val = st.session_state["detected_speakers"] or "—"
                st.markdown(f'<div class="ms-metric"><span class="val">{speaker_val}</span>'
                            f'<span class="lbl">Speakers</span></div>', unsafe_allow_html=True)
            with m3:
                mins, secs = int(dur // 60), int(dur % 60)
                dlabel = f"{mins}m {secs}s" if dur > 0 else "—"
                st.markdown(f'<div class="ms-metric"><span class="val">{dlabel}</span>'
                            f'<span class="lbl">Duration</span></div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="ms-panel"><div class="ms-panel-title">Diarized Transcript</div>',
                    unsafe_allow_html=True)

        dt = st.session_state["diarized_transcript"]
        if dt:
            parts = []
            for line in dt.split("\n"):
                s = line.strip()
                if not s:
                    continue
                if s.endswith(":") and not line.startswith("  "):
                    parts.append(f'<span class="spk">{html.escape(s)}</span>')
                else:
                    parts.append(f'<span class="line">{html.escape(s)}</span>')
            body = "\n".join(parts)
        elif st.session_state["status"] == "recording":
            live = st.session_state["live_text"].strip()
            body = (
                f'<span class="live">{html.escape(live)}</span>'
                if live else '<span class="live">● Recording… listening for speech.</span>'
            )
        elif st.session_state["status"] in ("transcribing", "diarizing"):
            body = '<span class="live">Processing audio…</span>'
        else:
            body = '<span class="dim">Transcript will appear here after processing.</span>'

        st.markdown(f'<div class="ms-transcript">{body}</div>', unsafe_allow_html=True)

        if dt:
            st.download_button("↓  Download Transcript", data=dt,
                               file_name="diarized_transcript.txt", mime="text/plain",
                               key="dl_transcript")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="ms-panel"><div class="ms-panel-title">Meeting Summary</div>',
                    unsafe_allow_html=True)

        summ = st.session_state["summary"]
        if summ:
            st.markdown(f'<div class="ms-summary">{summ}</div>', unsafe_allow_html=True)
            st.download_button("↓  Download Summary", data=summ,
                               file_name="meeting_summary.txt", mime="text/plain",
                               key="dl_summary")
        elif st.session_state["status"] == "summarizing":
            st.markdown('<div class="ms-summary" style="color:#3A3E4A;font-style:italic;">'
                        'Generating summary…</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ms-summary" style="color:#2A2E38;font-style:italic;">'
                        'Summary will appear here after processing.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        raw = st.session_state["raw_transcript"]
        if raw:
            with st.expander("Raw Whisper Transcript"):
                st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.78rem;'
                            f'line-height:1.75;color:#9A9DAA;">{raw}</div>',
                            unsafe_allow_html=True)


@st.fragment(run_every=0.5)
def _render_live_app():
    _drain_runtime_queues()
    _render_main_ui()


_render_live_app()
