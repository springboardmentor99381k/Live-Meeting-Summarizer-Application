import whisper
import sounddevice as sd
import numpy as np
import queue
from jiwer import wer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces
from datetime import datetime

# ── Model ──────────────────────────────────────────────────────────────────────
model = whisper.load_model("medium")

# ── Audio settings ─────────────────────────────────────────────────────────────
SAMPLERATE      = 16000
CHUNK_SEC       = 6
OVERLAP_SEC     = 1
CHUNK_SAMPLES   = SAMPLERATE * CHUNK_SEC
OVERLAP_SAMPLES = SAMPLERATE * OVERLAP_SEC

# ── VAD threshold ──────────────────────────────────────────────────────────────
# SILENCE_THRESH = 0.0  →  VAD disabled (safe default, accepts all audio)
# After running once with DEBUG_RMS=True, look at your speech RMS values and
# set SILENCE_THRESH to roughly half of your typical speech RMS.
# Example: speech RMS ≈ 0.04  →  set SILENCE_THRESH = 0.02
SILENCE_THRESH  = 0.0      # 0.0 = disabled
DEBUG_RMS       = True     # prints RMS per chunk to help you calibrate later

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

def rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(audio ** 2)))

def has_speech(audio: np.ndarray) -> bool:
    if SILENCE_THRESH <= 0.0:
        return True          # VAD disabled — always transcribe
    return rms(audio) > SILENCE_THRESH

def build_initial_prompt(recent: str, max_words: int = 30) -> str:
    words = recent.strip().split()
    return " ".join(words[-max_words:]) if words else ""

# ── Main ───────────────────────────────────────────────────────────────────────
print("🎤 Speak clearly (Whisper)... Press Ctrl+C to stop")
print(f"   VAD threshold : {SILENCE_THRESH} ({'disabled' if SILENCE_THRESH <= 0 else 'active'})")
print(f"   DEBUG_RMS     : {DEBUG_RMS}\n")

buffer          = np.empty((0,), dtype=np.float32)
full_transcript = ""
recent_text     = ""

try:
    with sd.InputStream(
        samplerate=SAMPLERATE,
        channels=1,
        dtype="float32",
        callback=callback,
        blocksize=int(SAMPLERATE * 0.1),
    ):
        while True:
            data   = q.get().flatten()
            buffer = np.concatenate((buffer, data))

            if len(buffer) >= CHUNK_SAMPLES:
                chunk  = buffer[:CHUNK_SAMPLES]
                buffer = buffer[CHUNK_SAMPLES - OVERLAP_SAMPLES:]

                chunk_rms = rms(chunk)
                if DEBUG_RMS:
                    print(f"[DEBUG] chunk RMS = {chunk_rms:.5f}", end="  ")

                if not has_speech(chunk):
                    if DEBUG_RMS:
                        print("SILENT, skipped")
                    continue

                if DEBUG_RMS:
                    print("transcribing...")

                result = model.transcribe(
                    chunk,
                    language="en",
                    task="transcribe",
                    temperature=0,
                    fp16=False,
                    condition_on_previous_text=True,
                    initial_prompt=build_initial_prompt(recent_text),
                    no_speech_threshold=0.6,
                    logprob_threshold=-1.0,
                    compression_ratio_threshold=2.4,
                )

                text = result["text"].strip()

                # Discard obvious hallucinations
                JUNK = {"thank you", "thanks for watching", "subscribe",
                        "you", ".", "...", "ugh", "um", "hmm", ""}
                if (
                    not text
                    or text.lower() in JUNK
                    or len(text.split()) < 2
                    or all(c in ".,!?- " for c in text)
                ):
                    if DEBUG_RMS:
                        print(f"   [filtered out] '{text}'")
                    continue

                print(">>", text)
                recent_text      = text
                full_transcript += text + " "

except KeyboardInterrupt:
    print("\nRecording stopped.")

# ── Save ───────────────────────────────────────────────────────────────────────
prediction = full_transcript.strip()
timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
filename   = f"whisper_transcript_{timestamp}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(prediction)
print(f"Transcript saved to: {filename}")

# ── WER ────────────────────────────────────────────────────────────────────────
try:
    with open("reference.txt", "r", encoding="utf-8") as f:
        reference = f.read().strip()
except FileNotFoundError:
    print("⚠  reference.txt not found.")
    reference = ""

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
])

if reference and prediction:
    error = wer(transform(reference), transform(prediction))
    print("\nReference Text:")
    print(reference)
    print("\nPredicted Transcript:")
    print(prediction)
    print(f"\nWER : {error:.4f}")
    print(f"WER%: {error * 100:.2f}%")
    if error <= 0.15:
        print("✅ Target met: WER ≤ 15%")
    else:
        print("❌ WER above 15%")
        print("\nCalibration tip: check [DEBUG] RMS values above while you spoke.")
        print("Set SILENCE_THRESH to ~50% of your typical speech RMS.")
        print("Example: speech RMS ≈ 0.04 → set SILENCE_THRESH = 0.02")
elif not prediction:
    print("\n⚠  Empty transcript — check the [DEBUG] lines above:")
    print("  • No [DEBUG] lines at all → mic not detected by sounddevice")
    print("  • [DEBUG] lines showed RMS but nothing transcribed → hallucination filter too strict")
else:
    print("\nReference text not available. WER not calculated.")