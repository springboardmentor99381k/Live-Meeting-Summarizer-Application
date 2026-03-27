import os
import json
import re
from datetime import datetime
from queue import Queue

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydub import AudioSegment
from werkzeug.utils import secure_filename

from meetmind_ai.config import settings
from meetmind_ai.core.audio_capture import AudioCapture
from meetmind_ai.core.diarization import Diarization
from meetmind_ai.core.emailer import Emailer
from meetmind_ai.core.exporter import Exporter
from meetmind_ai.core.merger import Merger
from meetmind_ai.core.stt_engine import STTEngine
from meetmind_ai.core.summarizer import Summarizer

app = Flask(__name__)

cors_origins = settings.CORS_ALLOWED_ORIGINS or ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173", "http://127.0.0.1:5173"]
CORS(
    app,
    resources={
        r"/api/*": {"origins": cors_origins},
        r"/": {"origins": cors_origins},
    },
)

os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)

app.config["AUDIO_CAPTURE"] = None
app.config["AUDIO_QUEUE"] = Queue()
app.config["LAST_WAV_PATH"] = ""
app.config["LAST_TRANSCRIPT"] = ""
app.config["LAST_DIARIZED_TRANSCRIPT"] = ""
app.config["LAST_DIARIZATION_PATH"] = ""
app.config["LAST_SUMMARY"] = ""
app.config["LAST_MEETING_TITLE"] = "Meeting Notes"
app.config["LAST_ATTENDEES"] = ""


def _live_transcript_callback(text: str) -> None:
    existing = app.config.get("LAST_TRANSCRIPT", "")
    if existing:
        app.config["LAST_TRANSCRIPT"] = f"{existing} {text}".strip()
    else:
        app.config["LAST_TRANSCRIPT"] = text.strip()


# Initialize lightweight instances at startup; heavy services are lazy.
stt_engine = None
diarizer = None
summarizer = None
exporter = Exporter("", "", "Meeting Notes", settings.OUTPUTS_DIR)
emailer = Emailer()
wer_eval = None
der_eval = None
rouge_eval = None


def _get_stt_engine():
    global stt_engine
    if stt_engine is None:
        stt_engine = STTEngine(app.config["AUDIO_QUEUE"], _live_transcript_callback)
    return stt_engine


def _get_diarizer():
    global diarizer
    if diarizer is None:
        diarizer = Diarization()
    return diarizer


def _get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer


def _get_wer_eval():
    global wer_eval
    if wer_eval is None:
        from meetmind_ai.evaluation.wer_evaluator import WEREvaluator

        wer_eval = WEREvaluator()
    return wer_eval


def _get_der_eval():
    global der_eval
    if der_eval is None:
        from meetmind_ai.evaluation.der_evaluator import DEREvaluator

        der_eval = DEREvaluator()
    return der_eval


def _get_rouge_eval():
    global rouge_eval
    if rouge_eval is None:
        from meetmind_ai.evaluation.rouge_evaluator import ROUGEEvaluator

        rouge_eval = ROUGEEvaluator()
    return rouge_eval


def _unique_temp_path(prefix: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ext = extension.lstrip(".")
    return os.path.join(settings.TEMP_DIR, f"{prefix}_{timestamp}.{ext}")


def _unique_output_path(prefix: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ext = extension.lstrip(".")
    return os.path.join(settings.OUTPUTS_DIR, f"{prefix}_{timestamp}.{ext}")


def _format_seconds_mss(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes}:{secs:02d}"


def _timestamps_to_lines(timestamps):
    lines = []
    for item in timestamps or []:
        start = float(item.get("start", 0.0))
        end = float(item.get("end", 0.0))
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        lines.append(f"[{_format_seconds_mss(start)} - {_format_seconds_mss(end)}] {text}")
    return "\n".join(lines)


def _build_conversation_text(transcript: str, timestamps, segments):
    """Adapt merge strategy based on how dense STT timestamp chunks are."""
    timestamp_count = len(timestamps or [])
    segment_count = len(segments or [])
    timestamp_lines = _timestamps_to_lines(timestamps)

    # If timestamp chunks are too sparse, distribute full transcript over diarization timeline
    # so more speaker turns are represented in output.
    sparse_timestamps = segment_count > 0 and timestamp_count < max(3, segment_count // 3)
    if sparse_timestamps:
        merger = Merger(transcript, segments)
        merge_mode = "duration-distributed"
    else:
        merger = Merger(timestamp_lines if timestamp_lines else transcript, segments)
        merge_mode = "timestamp-aligned"

    merged = merger.merge()
    conversation_text = merger.format_transcript(merged)
    return conversation_text, merge_mode


def _count_speakers_from_conversation(text: str) -> int:
    speaker_tags = re.findall(r"\bSPEAKER[_\s-]?\d+\b", text or "", flags=re.IGNORECASE)
    normalized = {tag.upper().replace(" ", "_").replace("-", "_") for tag in speaker_tags}
    return len(normalized)


def _infer_title_from_text(text: str) -> str:
    content = (text or "").strip()
    if not content:
        return "Meeting Notes"

    cleaned = re.sub(r"SPEAKER[_\s-]?\d+\s*\[[^\]]+\]:", "", content, flags=re.IGNORECASE)
    words = re.findall(r"[A-Za-z0-9']+", cleaned)
    if not words:
        return "Meeting Notes"

    title_words = words[:8]
    return " ".join(title_words).strip().title()


def _parse_clock_to_seconds(clock_text: str) -> float:
    text = (clock_text or "").strip()
    if not text:
        return 0.0

    parts = text.split(":")
    try:
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            return float(minutes * 60 + seconds)
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return float(hours * 3600 + minutes * 60 + seconds)
    except ValueError:
        return 0.0

    return 0.0


def _compute_duration_from_conversation(text: str) -> str:
    matches = re.findall(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(\d{1,2}:\d{2}(?::\d{2})?)\]", text or "")
    if not matches:
        return "0:00"

    min_start = float("inf")
    max_end = 0.0
    for start_text, end_text in matches:
        start_sec = _parse_clock_to_seconds(start_text)
        end_sec = _parse_clock_to_seconds(end_text)
        min_start = min(min_start, start_sec)
        max_end = max(max_end, end_sec)

    if min_start == float("inf"):
        return "0:00"

    duration = max(0.0, max_end - min_start)
    return _format_seconds_mss(duration)


def _extract_summary_sections(model_summary: str):
    text = (model_summary or "").strip()
    if not text:
        return "No executive summary generated.", "Not explicitly listed."

    exec_heading = re.search(r"Executive\s*Summary\s*:?,?", text, flags=re.IGNORECASE)
    key_heading = re.search(r"Key\s*Discussion\s*Points\s*:?,?", text, flags=re.IGNORECASE)

    exec_text = ""
    key_text = ""

    if exec_heading and key_heading:
        exec_start = exec_heading.end()
        key_start = key_heading.start()
        key_content_start = key_heading.end()
        if key_start >= exec_start:
            exec_text = text[exec_start:key_start].strip()
            key_text = text[key_content_start:].strip()
    elif key_heading:
        key_text = text[key_heading.end():].strip()
        exec_text = text[:key_heading.start()].strip()
    else:
        exec_text = text

    if not exec_text:
        exec_text = "No executive summary generated."
    if not key_text:
        key_text = "Not explicitly listed."

    return exec_text, key_text


@app.get("/")
def index():
    return jsonify({
        "service": "meetmind-ai-backend",
        "status": "ok",
        "api_base": "/api",
    })


@app.post("/api/start-recording")
def start_recording():
    global stt_engine

    existing_capture = app.config.get("AUDIO_CAPTURE")
    if existing_capture is not None:
        try:
            existing_capture.stop_recording()
        except Exception:
            pass

    if stt_engine is not None:
        try:
            stt_engine.stop_transcription()
        except Exception:
            pass

    audio_queue = Queue()
    capture = AudioCapture(audio_queue)
    stt_engine = STTEngine(audio_queue, _live_transcript_callback)

    app.config["LAST_TRANSCRIPT"] = ""
    capture.start_recording()
    stt_engine.start_transcription()

    app.config["AUDIO_CAPTURE"] = capture
    app.config["AUDIO_QUEUE"] = audio_queue

    return jsonify({"status": "recording_started", "transcription": "started"})


@app.post("/api/stop-recording")
def stop_recording():
    global stt_engine

    capture = app.config.get("AUDIO_CAPTURE")
    if capture is None:
        return jsonify({"error": "No active recording session."}), 400

    capture.stop_recording()
    if stt_engine is not None:
        stt_engine.stop_transcription()

    wav_path = _unique_temp_path("session", "wav")
    capture.save_wav(wav_path)

    app.config["LAST_WAV_PATH"] = wav_path
    app.config["AUDIO_CAPTURE"] = None

    return jsonify(
        {
            "status": "stopped",
            "wav_path": wav_path,
            "transcript": app.config.get("LAST_TRANSCRIPT", ""),
        }
    )


@app.post("/api/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Missing file field in multipart form data."}), 400

    file = request.files["file"]
    if file.filename is None or file.filename.strip() == "":
        return jsonify({"error": "No file selected."}), 400

    safe_name = secure_filename(file.filename)
    original_root, original_ext = os.path.splitext(safe_name)
    original_ext = original_ext.lower().lstrip(".") or "bin"
    safe_prefix = original_root or "upload"
    input_path = _unique_temp_path(safe_prefix, original_ext)

    try:
        file.save(input_path)
    except Exception as exc:
        return jsonify({"error": f"Could not save uploaded file: {exc}"}), 500

    ext = f".{original_ext}"

    if ext == ".wav":
        wav_path = input_path
    else:
        wav_path = _unique_temp_path(safe_prefix, "wav")
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(wav_path, format="wav")
        except Exception as exc:
            return jsonify({"error": f"Audio conversion to WAV failed: {exc}"}), 500

    app.config["LAST_WAV_PATH"] = wav_path
    return jsonify({"wav_path": wav_path})


@app.get("/api/live-transcript")
def live_transcript():
    return jsonify({"transcript": app.config.get("LAST_TRANSCRIPT", "")})


@app.post("/api/transcribe")
def transcribe():
    payload = request.get_json(silent=True) or {}
    wav_path = payload.get("wav_path", "")

    if not wav_path:
        return jsonify({"error": "Missing 'wav_path' in request body."}), 400

    transcript, timestamps = _get_stt_engine().transcribe_file(wav_path)
    app.config["LAST_TRANSCRIPT"] = transcript

    return jsonify({"transcript": transcript, "timestamps": timestamps})


@app.post("/api/diarize")
def diarize():
    payload = request.get_json(silent=True) or {}
    wav_path = payload.get("wav_path", "") or app.config.get("LAST_WAV_PATH", "")

    if not wav_path:
        return jsonify({"error": "Missing 'wav_path' and no previous WAV found."}), 400

    diarizer_instance = _get_diarizer()
    if not diarizer_instance.is_available():
        return jsonify({"error": f"Diarization unavailable: {diarizer_instance.last_error}"}), 503

    if not os.path.isfile(wav_path):
        return jsonify({"error": f"WAV file not found: {wav_path}"}), 404

    segments = diarizer_instance.run(wav_path)
    if not segments and diarizer_instance.last_error:
        return jsonify({"error": diarizer_instance.last_error, "segments": []}), 422

    diarization_path = _unique_output_path("diarization", "json")
    try:
        with open(diarization_path, "w", encoding="utf-8") as diarization_file:
            json.dump(segments, diarization_file, indent=2)
        app.config["LAST_DIARIZATION_PATH"] = diarization_path
    except OSError as exc:
        return jsonify({"error": f"Failed to save diarization output: {exc}", "segments": segments}), 500

    return jsonify({"segments": segments, "diarization_path": diarization_path})


@app.post("/api/wav-to-conversation")
def wav_to_conversation():
    payload = request.get_json(silent=True) or {}
    wav_path = payload.get("wav_path", "") or app.config.get("LAST_WAV_PATH", "")

    if not wav_path:
        return jsonify({"error": "Missing 'wav_path' and no previous WAV found."}), 400

    if not os.path.isfile(wav_path):
        return jsonify({"error": f"WAV file not found: {wav_path}"}), 404

    transcript, timestamps = _get_stt_engine().transcribe_file(wav_path)
    if not transcript:
        return jsonify({"error": "STT transcription failed or returned empty output."}), 422

    diarizer_instance = _get_diarizer()
    if not diarizer_instance.is_available():
        return jsonify({"error": f"Diarization unavailable: {diarizer_instance.last_error}"}), 503

    segments = diarizer_instance.run(wav_path)
    if not segments:
        reason = diarizer_instance.last_error or "No diarization segments were generated."
        return jsonify({"error": reason}), 422

    conversation_text, merge_mode = _build_conversation_text(transcript, timestamps, segments)

    if not conversation_text.strip():
        return jsonify({"error": "Could not build conversation text from diarization + transcript."}), 422

    conversation_txt_path = _unique_output_path("conversation", "txt")
    try:
        with open(conversation_txt_path, "w", encoding="utf-8") as conversation_file:
            conversation_file.write(conversation_text)
    except OSError as exc:
        return jsonify({"error": f"Failed to save conversation txt: {exc}"}), 500

    app.config["LAST_TRANSCRIPT"] = transcript
    app.config["LAST_DIARIZED_TRANSCRIPT"] = conversation_text
    app.config["LAST_WAV_PATH"] = wav_path

    return jsonify(
        {
            "wav_path": wav_path,
            "conversation_text": conversation_text,
            "conversation_txt_path": conversation_txt_path,
            "segments": segments,
            "merge_mode": merge_mode,
        }
    )


@app.post("/api/run-pipeline")
def run_pipeline():
    """Run STT -> Diarization -> Summarization using current/live WAV input."""
    payload = request.get_json(silent=True) or {}
    wav_path = payload.get("wav_path", "") or app.config.get("LAST_WAV_PATH", "")
    meeting_title = payload.get("meeting_title", "")
    attendees = payload.get("attendees", "")

    if not wav_path:
        return jsonify({"error": "Missing 'wav_path' and no previous WAV found."}), 400

    if not os.path.isfile(wav_path):
        return jsonify({"error": f"WAV file not found: {wav_path}"}), 404

    transcript, timestamps = _get_stt_engine().transcribe_file(wav_path)
    if not transcript:
        return jsonify({"error": "STT transcription failed or returned empty output."}), 422

    diarizer_instance = _get_diarizer()
    if not diarizer_instance.is_available():
        return jsonify({"error": f"Diarization unavailable: {diarizer_instance.last_error}"}), 503

    segments = diarizer_instance.run(wav_path)
    if not segments:
        reason = diarizer_instance.last_error or "No diarization segments were generated."
        return jsonify({"error": reason}), 422

    conversation_text, merge_mode = _build_conversation_text(transcript, timestamps, segments)
    if not conversation_text.strip():
        return jsonify({"error": "Could not build conversation text from diarization + transcript."}), 422

    conversation_txt_path = _unique_output_path("conversation", "txt")
    diarization_path = _unique_output_path("diarization", "json")
    try:
        with open(conversation_txt_path, "w", encoding="utf-8") as conversation_file:
            conversation_file.write(conversation_text)
        with open(diarization_path, "w", encoding="utf-8") as diarization_file:
            json.dump(segments, diarization_file, indent=2)
    except OSError as exc:
        return jsonify({"error": f"Failed to save pipeline outputs: {exc}"}), 500

    speaker_count = _count_speakers_from_conversation(conversation_text)
    duration_text = _compute_duration_from_conversation(conversation_text)
    resolved_meeting_title = meeting_title.strip() if isinstance(meeting_title, str) else ""
    if not resolved_meeting_title:
        resolved_meeting_title = _infer_title_from_text(conversation_text)

    model_summary = _get_summarizer().summarize(conversation_text, resolved_meeting_title, attendees)
    executive_summary, key_points = _extract_summary_sections(model_summary)
    summary = (
        f"Title: {resolved_meeting_title}\n"
        f"Duration: {duration_text}\n"
        f"No of Speakers: {speaker_count}\n\n"
        "Executive Summary:\n"
        f"{executive_summary}\n\n"
        "Key Discussion Points:\n"
        f"{key_points}"
    )

    app.config["LAST_WAV_PATH"] = wav_path
    app.config["LAST_TRANSCRIPT"] = transcript
    app.config["LAST_DIARIZED_TRANSCRIPT"] = conversation_text
    app.config["LAST_DIARIZATION_PATH"] = diarization_path
    app.config["LAST_SUMMARY"] = summary
    app.config["LAST_MEETING_TITLE"] = resolved_meeting_title or "Meeting Notes"
    app.config["LAST_ATTENDEES"] = attendees

    return jsonify(
        {
            "wav_path": wav_path,
            "transcript": transcript,
            "segments": segments,
            "diarization_path": diarization_path,
            "conversation_text": conversation_text,
            "conversation_txt_path": conversation_txt_path,
            "summary": summary,
            "meeting_title": resolved_meeting_title,
            "speaker_count": speaker_count,
            "duration": duration_text,
            "merge_mode": merge_mode,
            "modules": {
                "stt": {"status": "ok", "transcript_chars": len(transcript)},
                "diarization": {"status": "ok", "segments": len(segments)},
                "summarization": {"status": "ok", "summary_chars": len(summary)},
            },
        }
    )


@app.post("/api/merge")
def merge():
    payload = request.get_json(silent=True) or {}
    transcript = payload.get("transcript", "")
    segments = payload.get("segments", [])

    merger = Merger(transcript, segments)
    merged = merger.merge()
    diarized_transcript = merger.format_transcript(merged)

    app.config["LAST_DIARIZED_TRANSCRIPT"] = diarized_transcript

    return jsonify({"diarized_transcript": diarized_transcript, "merged": merged})


@app.post("/api/summarize")
def summarize():
    payload = request.get_json(silent=True) or {}
    diarized_transcript = payload.get("diarized_transcript", payload.get("transcript", ""))
    if not diarized_transcript:
        conversation_txt_path = payload.get("conversation_txt_path", "")
        if conversation_txt_path and os.path.isfile(conversation_txt_path):
            try:
                with open(conversation_txt_path, "r", encoding="utf-8") as txt_file:
                    diarized_transcript = txt_file.read()
            except OSError as exc:
                return jsonify({"error": f"Could not read conversation txt file: {exc}"}), 400

    if not diarized_transcript:
        diarized_transcript = app.config.get("LAST_DIARIZED_TRANSCRIPT", "")

    if not diarized_transcript:
        return jsonify({"error": "Missing transcript data for summarization."}), 400

    meeting_title = payload.get("meeting_title", "")
    attendees = payload.get("attendees", "")
    speaker_count = _count_speakers_from_conversation(diarized_transcript)
    duration_text = _compute_duration_from_conversation(diarized_transcript)
    resolved_meeting_title = meeting_title.strip() if isinstance(meeting_title, str) else ""
    if not resolved_meeting_title:
        resolved_meeting_title = _infer_title_from_text(diarized_transcript)

    model_summary = _get_summarizer().summarize(diarized_transcript, resolved_meeting_title, attendees)
    executive_summary, key_points = _extract_summary_sections(model_summary)
    summary = (
        f"Title: {resolved_meeting_title}\n"
        f"Duration: {duration_text}\n"
        f"No of Speakers: {speaker_count}\n\n"
        "Executive Summary:\n"
        f"{executive_summary}\n\n"
        "Key Discussion Points:\n"
        f"{key_points}"
    )

    app.config["LAST_SUMMARY"] = summary
    app.config["LAST_MEETING_TITLE"] = resolved_meeting_title or "Meeting Notes"
    app.config["LAST_ATTENDEES"] = attendees
    app.config["LAST_DIARIZED_TRANSCRIPT"] = diarized_transcript

    return jsonify(
        {
            "summary": summary,
            "meeting_title": resolved_meeting_title,
            "speaker_count": speaker_count,
            "duration": duration_text,
        }
    )


@app.get("/api/export")
def export():
    fmt = (request.args.get("format", "").strip().lower())
    if fmt not in {"md", "pdf", "docx"}:
        return jsonify({"error": "Invalid format. Use one of: md, pdf, docx."}), 400

    summary = app.config.get("LAST_SUMMARY", "")
    diarized_transcript = app.config.get("LAST_DIARIZED_TRANSCRIPT", "")
    meeting_title = app.config.get("LAST_MEETING_TITLE", "Meeting Notes")

    global exporter
    exporter = Exporter(summary, diarized_transcript, meeting_title, settings.OUTPUTS_DIR)

    if fmt == "md":
        file_path = exporter.export_markdown()
    elif fmt == "pdf":
        file_path = exporter.export_pdf()
    else:
        file_path = exporter.export_docx()

    if not file_path:
        return jsonify({"error": "Export failed. Check server logs for details."}), 500

    return send_file(file_path, as_attachment=True)


@app.post("/api/evaluate")
def evaluate():
    payload = request.get_json(silent=True) or {}

    reference = payload.get("reference", payload.get("reference_text", ""))
    hypothesis = payload.get("hypothesis", payload.get("hypothesis_text", ""))
    reference_summary = payload.get("reference_summary", "")
    generated_summary = payload.get("generated_summary", "")

    wer_scores = _get_wer_eval().compute(reference, hypothesis)
    rouge_scores = _get_rouge_eval().compute(reference_summary, generated_summary)

    return jsonify({
        "wer": wer_scores,
        "rouge": rouge_scores,
    })


@app.post("/api/email")
def email():
    payload = request.get_json(silent=True) or {}
    recipient = payload.get("recipient", "")
    attachment_path = payload.get("attachment_path")

    if not recipient:
        return jsonify({"error": "Missing 'recipient' in request body."}), 400

    subject = f"MeetMind AI - {app.config.get('LAST_MEETING_TITLE', 'Meeting Summary')}"
    body = app.config.get("LAST_SUMMARY", "")
    if not body:
        body = app.config.get("LAST_DIARIZED_TRANSCRIPT", "")

    sent = emailer.send(recipient, subject, body, attachment_path=attachment_path)
    if not sent:
        return jsonify({"error": "Email sending failed. Check server logs for details."}), 500

    return jsonify({"status": "sent"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
