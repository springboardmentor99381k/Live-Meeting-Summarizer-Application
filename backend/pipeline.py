import queue
import threading

# -----------------------------
# GLOBALS
# -----------------------------
task_queue = queue.Queue()

result = {
    "transcript": "",
    "diarized": "",
    "summary": "",
    "status": "Idle"
}

lock = threading.Lock()


# -----------------------------
# TASK SUBMISSION FUNCTION
# -----------------------------
def submit_task(audio_path):
    task_queue.put({
        "type": "process",
        "audio": audio_path
    })


# -----------------------------
# WORKER THREAD
# -----------------------------
def worker():
    while True:
        task = task_queue.get()

        try:
            if task["type"] == "process":

                from stt.vosk_transcriber import transcribe_audio
                from summarization.summarizer import summarize_text

                audio = task["audio"]
                # ---------------- TRANSCRIPTION ----------------
                with lock:
                    result["status"] = "Transcribing..."
                    result["transcript"] = ""
                    result["diarized"] = ""
                    result["summary"] = ""

                transcript = transcribe_audio(audio)

                with lock:
                    result["transcript"] = transcript

                # ---------------- DIARIZATION ----------------
                # ---------------- DIARIZATION (SKIPPED) ----------------
                with lock:
                    result["status"] = "Preparing transcript..."

                diarized = transcript

                with lock:
                    result["diarized"] = diarized
                # ---------------- SUMMARIZATION ----------------
                with lock:
                    result["status"] = "Summarizing..."

                summary = summarize_text(diarized)

                with lock:
                    result["summary"] = summary
                    result["status"] = "Done"

        except Exception as e:
            with lock:
                result["status"] = f"Error: {str(e)}"

        finally:
            task_queue.task_done()


# -----------------------------
# START WORKER THREAD
# -----------------------------
threading.Thread(target=worker, daemon=True).start()