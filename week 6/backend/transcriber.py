import os
import logging
import time
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache and lock for thread safety
model = None
model_lock = threading.Lock()


def load_model(device="cpu"):
    """Load Whisper model once and cache globally."""
    global model

    with model_lock:
        if model is not None:
            return model

        try:
            import whisper
            logger.info("Loading model (only once)")
            start_time = time.time()
            model = whisper.load_model("tiny", device=device)
            load_time = time.time() - start_time
            logger.info("Whisper model loaded successfully in %.2f seconds", load_time)
            return model

        except ImportError:
            logger.error("Failed to import whisper. Install with: pip install openai-whisper")
            model = None
            return None
        except Exception as e:
            logger.error("Failed to load Whisper model: %s", str(e))
            model = None
            return None


def transcribe_chunk(audio_path: str, device: str = "cpu") -> str:
    """
    Transcribe audio chunk using OpenAI Whisper.
    Returns the transcribed text or error message on failure.
    """
    if not os.path.exists(audio_path):
        logger.error("Audio file not found: %s", audio_path)
        return "Audio file not found"

    try:
        model = load_model(device=device)

        if model is None:
            logger.error("Whisper model unavailable; skipping transcription.")
            return ""

        logger.info("Transcribing file: %s", audio_path)
        start_time = time.time()

        result = model.transcribe(audio_path, fp16=False)

        transcribe_time = time.time() - start_time
        text = result.get("text", "").strip()

        if not text:
            text = "[No speech detected]"

        logger.info("Transcription result: %s", text)
        logger.info("Text length: %d", len(text))
        logger.info("Transcription completed in %.2f seconds", transcribe_time)

        return text

    except Exception as e:
        logger.error("Transcription failed for %s: %s", audio_path, str(e))
        return ""