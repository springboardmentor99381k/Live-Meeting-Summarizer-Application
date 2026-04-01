import streamlit as st
import tempfile
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from Diarization.diarizationcopy import run_diarization
from faster_whisper import WhisperModel

fast_model = WhisperModel("tiny", compute_type="int8")


# ════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG & STYLES  (UI only — no logic below this block)
# ════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="MEET MIND· AI Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background: #080b14;
    color: #dde3f0;
}
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem 2rem; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid rgba(99,140,255,0.12);
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

/* ── Sidebar brand ── */
.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 1.4rem;
    border-bottom: 1px solid rgba(99,140,255,0.13);
    margin-bottom: 1.4rem;
}
.sb-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg,#3a5ccc,#5b8dee);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.sb-title { font-size: 1rem; font-weight: 700; color: #c8d8ff; line-height: 1.1; }
.sb-sub   { font-size: 0.62rem; color: rgba(150,170,230,0.45); letter-spacing: 0.04em; }

/* ── Sidebar section labels ── */
.sb-label {
    font-size: 0.62rem; font-weight: 600;
    letter-spacing: 0.13em; text-transform: uppercase;
    color: rgba(140,165,240,0.45);
    margin: 1.2rem 0 0.45rem 0;
}

/* ── Divider ── */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg,transparent,rgba(80,120,255,0.18),transparent);
    margin: 1rem 0;
}

/* ── Radio ── */
div[data-testid="stRadio"] > div { flex-direction: column !important; gap: 6px; }
div[data-testid="stRadio"] label {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(99,140,255,0.15) !important;
    border-radius: 10px !important;
    padding: 9px 14px !important;
    color: #99aad8 !important;
    font-size: 0.88rem !important;
    transition: all 0.18s;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(80,120,255,0.10) !important;
    border-color: rgba(99,140,255,0.35) !important;
    color: #c8d8ff !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(80,120,255,0.04);
    border: 1.5px dashed rgba(80,120,255,0.25);
    border-radius: 12px;
    padding: 0.8rem;
}

/* ── Audio input ── */
[data-testid="stAudioInput"] {
    background: rgba(60,160,255,0.04);
    border: 1.5px dashed rgba(60,160,255,0.22);
    border-radius: 12px;
    padding: 0.8rem;
}

/* ── All buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#2d4fc5,#4a7de8) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 11px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.62rem 1.4rem !important;
    width: 100% !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 18px rgba(60,100,240,0.22) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(60,100,240,0.36) !important;
}
.stButton > button:disabled {
    opacity: 0.38 !important;
    transform: none !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: rgba(60,100,220,0.14) !important;
    border: 1px solid rgba(80,120,255,0.28) !important;
    color: #89aaff !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.8rem !important;
    width: 100% !important;
    transition: all 0.18s !important;
}
.stDownloadButton > button:hover {
    background: rgba(60,100,220,0.28) !important;
    border-color: rgba(80,120,255,0.55) !important;
    color: #b8d0ff !important;
}

/* ── Text input ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(80,120,255,0.2) !important;
    border-radius: 10px !important;
    color: #c0d4ff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(80,120,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(80,120,255,0.12) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #0d1120;
    border-radius: 12px;
    padding: 5px; gap: 4px;
    border: 1px solid rgba(80,120,255,0.12);
    margin-bottom: 1.2rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: rgba(150,175,235,0.6) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
    transition: all 0.18s;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(60,100,220,0.22) !important;
    color: #a8c4ff !important;
}

/* ── Spinners / alerts ── */
[data-testid="stSpinner"] { color: #89aaff !important; }
[data-testid="stAlert"] { border-radius: 12px !important; }

/* ── Subheaders ── */
h2, h3, .stSubheader {
    font-family: 'Outfit', sans-serif !important;
    color: #c8d8ff !important;
    letter-spacing: -0.02em !important;
}

/* ── st.text output ── */
.stText, pre {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    color: #99b4d8 !important;
    background: #080c18 !important;
    border: 1px solid rgba(80,120,255,0.10) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    line-height: 1.75 !important;
}

/* ── Hero header ── */
.main-hero {
    background: linear-gradient(135deg,#0e1425,#111830,#0c1520);
    border: 1px solid rgba(80,120,255,0.14);
    border-radius: 18px;
    padding: 2rem 2.4rem 1.8rem;
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.main-hero::after {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle,rgba(70,120,255,0.09) 0%,transparent 65%);
    border-radius: 50%; pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(80,120,255,0.12);
    border: 1px solid rgba(80,120,255,0.25);
    color: #89aaff;
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.10em; text-transform: uppercase;
    padding: 4px 12px; border-radius: 100px;
    margin-bottom: 0.85rem;
}
.live-dot {
    width: 6px; height: 6px;
    background: #5b8dee; border-radius: 50%;
    animation: blink 2s ease-in-out infinite;
    display: inline-block;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.hero-title {
    font-size: 2rem; font-weight: 700;
    letter-spacing: -0.03em; color: #dde8ff;
    margin: 0 0 0.3rem 0; line-height: 1.15;
}
.hero-title span {
    background: linear-gradient(90deg,#7aaeff,#a5c4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { font-size: 0.92rem; color: rgba(170,190,240,0.45); font-weight: 300; margin: 0; }

/* ── Metric cards ── */
.metric-card {
    background: #0d1220;
    border: 1px solid rgba(80,120,255,0.13);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg,#3a5ccc,#5b8dee);
    border-radius: 14px 14px 0 0;
}
.metric-icon { font-size: 1.2rem; margin-bottom: 0.45rem; display: block; }
.metric-label {
    font-size: 0.62rem; font-weight: 500;
    color: rgba(140,165,230,0.45);
    letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.25rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem; font-weight: 500; color: #c0d4ff; line-height: 1;
}
.metric-value-sm {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem; font-weight: 500; color: #c0d4ff;
    line-height: 1.3; word-break: break-all;
}

/* ── Output card wrapper ── */
.output-card {
    background: #0d1220;
    border: 1px solid rgba(80,120,255,0.13);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
}

/* ── Summary highlight ── */
.summary-highlight {
    background: linear-gradient(135deg,#0e1830,#111e3a);
    border: 1px solid rgba(80,130,255,0.2);
    border-left: 3px solid #4a7de8;
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    font-size: 0.93rem; line-height: 1.78;
    color: #c8d8f8;
    white-space: pre-wrap;
}

/* ── Speaker bars ── */
.spk-row { margin-bottom: 0.75rem; }
.spk-name { font-size: 0.75rem; font-weight: 500; color: #99b4e8; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; }
.spk-bar-bg { background: rgba(80,120,255,0.10); border-radius: 100px; height: 7px; overflow: hidden; margin-bottom: 3px; }
.spk-bar-fill { background: linear-gradient(90deg,#3a5ccc,#5b8dee); height: 100%; border-radius: 100px; }
.spk-pct { font-size: 0.68rem; color: rgba(140,170,240,0.5); font-family: 'JetBrains Mono', monospace; }

/* ── Download card grid ── */
.dl-card {
    background: #0d1220;
    border: 1px solid rgba(80,120,255,0.14);
    border-radius: 12px;
    padding: 0.9rem 0.8rem;
    text-align: center;
    margin-bottom: 4px;
}
.dl-icon { font-size: 1.4rem; margin-bottom: 5px; }
.dl-name {
    font-size: 0.65rem; font-weight: 500;
    color: rgba(140,165,240,0.55);
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 9px;
}

/* ── Scrollable transcript box ── */
.scroll-box {
    background: #080c18;
    border: 1px solid rgba(80,120,255,0.10);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    max-height: 400px; overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; line-height: 1.78;
    color: #99b4d8; white-space: pre-wrap;
}
.scroll-box::-webkit-scrollbar { width: 5px; }
.scroll-box::-webkit-scrollbar-track { background: transparent; }
.scroll-box::-webkit-scrollbar-thumb { background: rgba(80,120,255,0.2); border-radius: 10px; }

/* ── Diarization lines ── */
.diar-line {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(80,120,255,0.07);
}
.diar-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: rgba(120,150,220,0.4);
    min-width: 105px; padding-top: 3px; flex-shrink: 0;
}
.diar-badge {
    font-size: 0.67rem; font-weight: 600;
    padding: 3px 8px; border-radius: 100px;
    background: rgba(60,100,220,0.18);
    border: 1px solid rgba(80,120,255,0.25);
    color: #89aaff; white-space: nowrap; flex-shrink: 0;
}
.diar-text { font-size: 0.85rem; color: #b0c4e8; line-height: 1.55; padding-top: 2px; }

/* ── Empty state ── */
.empty-state {
    text-align: center; padding: 4rem 2rem;
    color: rgba(140,165,230,0.35);
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1rem; font-weight: 500; color: rgba(160,185,245,0.4); margin-bottom: 0.4rem; }
.empty-sub { font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  BACKEND FUNCTIONS — ORIGINAL, UNTOUCHED
# ════════════════════════════════════════════════════════════════════════════

def transcribe_audio(file_path):
    segments, _ = fast_model.transcribe(file_path)
    text = ""
    for segment in segments:
        text += segment.text + " "
    return text


def summarize_text(transcript_text):
    from transformers import pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    if len(transcript_text.split()) < 30:
        return "Summary cannot be generated (text too short)."

    max_chunk = 400
    words = transcript_text.split()
    chunks = [" ".join(words[i:i+max_chunk]) for i in range(0, len(words), max_chunk)]

    final_summary = ""
    for chunk in chunks:
        try:
            result = summarizer(chunk, max_length=80, min_length=25, do_sample=False)
            final_summary += result[0]["summary_text"] + "\n"
        except:
            continue

    return final_summary if final_summary.strip() else "Summary could not be generated."


def save_transcription(text):
    file_name = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(file_name, "w") as f:
        f.write("TRANSCRIPTION:\n\n")
        f.write(text)
    return file_name


def save_diarization(diarization_text):
    file_name = f"diarization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(file_name, "w") as f:
        f.write("DIARIZATION:\n\n")
        f.write(diarization_text)
    return file_name


def save_summary(summary_text):
    file_name = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("SUMMARY REPORT\n\n")
        f.write(summary_text)
    return file_name


def save_pdf(transcription, diarization, summary):
    file_name = f"meeting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("AI Meeting Report", styles['Title']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Summary", styles['Heading2']))
    content.append(Spacer(1, 8))
    for line in summary.split("\n"):
        content.append(Paragraph(line, styles['Normal']))
        content.append(Spacer(1, 6))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Transcription", styles['Heading2']))
    content.append(Spacer(1, 8))
    for line in transcription.split("."):
        content.append(Paragraph(line, styles['Normal']))
        content.append(Spacer(1, 6))
    content.append(Spacer(1, 12))
    content.append(Paragraph("Diarization", styles['Heading2']))
    content.append(Spacer(1, 8))
    for line in diarization.split("\n"):
        content.append(Paragraph(line, styles['Normal']))
        content.append(Spacer(1, 6))
    doc.build(content)
    return file_name


def send_email(receiver_email, file_path):
    import smtplib
    from email.message import EmailMessage

    sender_email = "example123@gmail.com"
    sender_password = "password123"

    msg = EmailMessage()
    msg['Subject'] = 'Meeting Summary'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content('Attached is your meeting summary.')

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream',
                           filename=os.path.basename(file_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR  (UI layout only — all logic variables preserved)
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sb-icon">🎙️</div>
        <div>
            <div class="sb-title">MEET MIND</div>
            <div class="sb-sub">AI Meeting Summarizer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">🎵 Input method</div>', unsafe_allow_html=True)

    # ── original variable name preserved ──
    option = st.radio("Choose Input Method:", ["Upload Audio", "Live Recording"],
                      label_visibility="collapsed")

    file_path = None

    if option == "Upload Audio":
        st.markdown('<div class="sb-label">📁 Audio file</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"],
                                         label_visibility="collapsed")
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                file_path = tmp.name
            st.success("✓ File ready")

    elif option == "Live Recording":
        st.markdown('<div class="sb-label">🔴 Record audio</div>', unsafe_allow_html=True)
        audio_file = st.audio_input("Record Audio", label_visibility="collapsed")
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(audio_file.read())
                file_path = tmp.name
            st.success("✓ Recording ready")

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-label">⚙️ Process</div>', unsafe_allow_html=True)
    process_btn = st.button("▶  Process Audio", disabled=(file_path is None))

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # ── Email — original logic untouched ──
    st.markdown('<div class="sb-label">📧 Send Full PDF Report via Email</div>', unsafe_allow_html=True)
    receiver = st.text_input("Enter Email", placeholder="name@example.com",
                             label_visibility="collapsed")

    if st.button("✉  Send Email"):
        if receiver:
            if "FullReport_pdf_file" in st.session_state:
                send_email(receiver, st.session_state.FullReport_pdf_file)
                st.success("Email Sent!")
            else:
                st.error("Please process audio first.")
        else:
            st.warning("Please enter email")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN PAGE HEADER
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-hero">
    <div class="hero-eyebrow"><span class="live-dot"></span> AI-Powered · Real-Time Processing</div>
    <h1 class="hero-title">Meeting Intelligence <span>Dashboard</span></h1>
    <p class="hero-sub">Transcribe, diarize, and summarize your meetings automatically.</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  PROCESS AUDIO — original logic, zero changes
# ════════════════════════════════════════════════════════════════════════════

if file_path and process_btn:

    with st.spinner("Transcribing..."):
        transcription = transcribe_audio(file_path)

    with st.spinner("Diarization..."):
        diarization = run_diarization(file_path)

    with st.spinner("Summarizing..."):
        summary = summarize_text(transcription)

    # Analytics — original logic
    lines = [l for l in diarization.split("\n") if l.strip()]
    total_lines = len(lines)
    total_words = 0
    speaker_words = {}

    for line in lines:
        try:
            text_part = line.split(":", 1)[-1]
            words = text_part.split()
            total_words += len(words)
            speaker = line.split("]")[1].split(":")[0].strip()
            if speaker not in speaker_words:
                speaker_words[speaker] = 0
            speaker_words[speaker] += len(words)
        except:
            continue

    total_speakers = len(speaker_words)
    most_active_speaker = max(speaker_words, key=speaker_words.get) if speaker_words else "N/A"

    # Summary block — original logic
    summary_block = f"""
       🧾 Summary

        Main Discussion Points:
        {summary}
        Speaker Contributions:
         """
    for speaker, words in speaker_words.items():
        percent = (words / total_words) * 100 if total_words else 0
        summary_block += f"{speaker} : {percent:.2f}%\n"

    summary_block += f"""
        
         Meeting Analytics:
        Total Speakers: {total_speakers}
        Total Transcript Lines: {total_lines}
        Total Words Spoken: {total_words}
        Most Active Speaker: {most_active_speaker}
        """

    # Save to session — original variable names
    st.session_state.transcription_file = save_transcription(transcription)
    st.session_state.diarization_file   = save_diarization(diarization)
    st.session_state.summary_file       = save_summary(summary_block)
    st.session_state.FullReport_pdf_file = save_pdf(transcription, diarization, summary_block)

    # Also cache display data
    st.session_state._transcription  = transcription
    st.session_state._diarization    = diarization
    st.session_state._summary        = summary
    st.session_state._summary_block  = summary_block
    st.session_state._speaker_words  = speaker_words
    st.session_state._total_words    = total_words
    st.session_state._total_speakers = total_speakers
    st.session_state._total_lines    = total_lines
    st.session_state._most_active    = most_active_speaker

    st.success("Processing Complete!")


# ════════════════════════════════════════════════════════════════════════════
#  RESULTS DISPLAY
# ════════════════════════════════════════════════════════════════════════════

if "_transcription" not in st.session_state:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🎙️</div>
        <div class="empty-title">No results yet</div>
        <div class="empty-sub">Upload or record audio in the sidebar, then click Process Audio.</div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Metric cards ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <span class="metric-icon">👥</span>
            <div class="metric-label">Total Speakers</div>
            <div class="metric-value">{st.session_state._total_speakers}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <span class="metric-icon">💬</span>
            <div class="metric-label">Words Spoken</div>
            <div class="metric-value">{st.session_state._total_words:,}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <span class="metric-icon">📋</span>
            <div class="metric-label">Transcript Lines</div>
            <div class="metric-value">{st.session_state._total_lines}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <span class="metric-icon">🏆</span>
            <div class="metric-label">Most Active</div>
            <div class="metric-value-sm">{st.session_state._most_active}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📝  Summary", "🗣️  Transcription", "👥  Diarization"])

    # ── Tab 1 — Summary ───────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.subheader("🧠 AI-Generated Summary")

        # Render original summary_block in the highlight box
        st.markdown(
            f'<div class="summary-highlight">{st.session_state._summary_block}</div>',
            unsafe_allow_html=True,
        )

        # Visual speaker bars (bonus — additive only)
        if st.session_state._speaker_words:
            st.markdown("#### 🎤 Speaker Contributions")
            for spk, wc in st.session_state._speaker_words.items():
                pct = (wc / st.session_state._total_words * 100) if st.session_state._total_words else 0
                st.markdown(f"""
                <div class="spk-row">
                    <div class="spk-name">{spk}</div>
                    <div class="spk-bar-bg"><div class="spk-bar-fill" style="width:{pct:.1f}%"></div></div>
                    <div class="spk-pct">{pct:.1f}% · {wc} words</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 2 — Transcription ─────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.subheader("📄 Full Transcription")
        st.markdown(
            f'<div class="scroll-box">{st.session_state._transcription}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 3 — Diarization ───────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="output-card">', unsafe_allow_html=True)
        st.subheader("👥 Speaker Diarization")

        raw_lines = [l for l in st.session_state._diarization.split("\n") if l.strip()]
        if raw_lines:
            html = ""
            for line in raw_lines:
                try:
                    time_part    = line.split("]")[0].replace("[", "").strip()
                    rest         = line.split("]", 1)[1].strip()
                    speaker_part = rest.split(":")[0].strip()
                    text_part    = rest.split(":", 1)[1].strip() if ":" in rest else ""
                    html += f"""<div class="diar-line">
                        <div class="diar-time">[{time_part}]</div>
                        <div class="diar-badge">{speaker_part}</div>
                        <div class="diar-text">{text_part}</div>
                    </div>"""
                except:
                    html += f'<div class="diar-line"><div class="diar-text">{line}</div></div>'
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("No diarization data available.")

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  DOWNLOAD SECTION — original logic, redesigned layout
# ════════════════════════════════════════════════════════════════════════════

if "transcription_file" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📥 Download Files")

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.markdown('<div class="dl-card"><div class="dl-icon">📝</div><div class="dl-name">Transcription</div>', unsafe_allow_html=True)
        with open(st.session_state.transcription_file, "rb") as f:
            st.download_button("Download", f, file_name=st.session_state.transcription_file,
                               use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="dl-card"><div class="dl-icon">👥</div><div class="dl-name">Diarization</div>', unsafe_allow_html=True)
        with open(st.session_state.diarization_file, "rb") as f:
            st.download_button("Download", f, file_name=st.session_state.diarization_file,
                               use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with d3:
        st.markdown('<div class="dl-card"><div class="dl-icon">📄</div><div class="dl-name">Summary</div>', unsafe_allow_html=True)
        with open(st.session_state.summary_file, "rb") as f:
            st.download_button("Download", f, file_name=st.session_state.summary_file,
                               use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with d4:
        st.markdown('<div class="dl-card"><div class="dl-icon">📑</div><div class="dl-name">PDF Report</div>', unsafe_allow_html=True)
        with open(st.session_state.FullReport_pdf_file, "rb") as f:
            st.download_button("Download", f, file_name=st.session_state.FullReport_pdf_file,
                               use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)