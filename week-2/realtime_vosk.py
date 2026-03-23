import queue
import sounddevice as sd
import json
import numpy as np
from vosk import Model, KaldiRecognizer
from jiwer import wer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces
from datetime import datetime

# ── Device & sample rate ───────────────────────────────────────────────────────
device_info = sd.query_devices(kind='input')
samplerate  = int(device_info['default_samplerate'])
print(f"Using device  : {device_info['name']}")
print(f"Using samplerate: {samplerate} Hz")

# ── Vosk model ─────────────────────────────────────────────────────────────────
# Use the larger model for better accuracy if available:
#   vosk-model-en-us-0.22  (recommended, ~1.8 GB)
#   vosk-model-small-en-us-0.15  (fast, smaller, less accurate)
model = Model("vosk-model-small-en-us-0.15")
rec   = KaldiRecognizer(model, samplerate)
rec.SetWords(True)

# ── VAD settings ───────────────────────────────────────────────────────────────
# Set to 0.0 to disable. Once working, check [DEBUG] RMS values while speaking
# and set to ~50% of your typical speech RMS to skip silent chunks.
SILENCE_THRESH = 0.0     # 0.0 = disabled (safe default)
DEBUG_RMS      = True    # print RMS per block for calibration

# ── Audio queue ────────────────────────────────────────────────────────────────
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def rms_from_bytes(data: bytes) -> float:
    """Compute RMS from raw int16 PCM bytes."""
    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return float(np.sqrt(np.mean(audio ** 2)))

def has_speech(data: bytes) -> bool:
    if SILENCE_THRESH <= 0.0:
        return True
    return rms_from_bytes(data) > SILENCE_THRESH

# ── Known Vosk hallucinations to filter ───────────────────────────────────────
JUNK_PHRASES = {
    "huh", "uh", "um", "ah", "oh", "the", "a", "i",
    "thank you", "thanks", "bye", "okay", "ok",
}

def is_junk(text: str) -> bool:
    t = text.strip().lower()
    return (
        not t
        or t in JUNK_PHRASES
        or len(t.split()) < 2          # single-word outputs are usually noise
    )

# ── Main ───────────────────────────────────────────────────────────────────────
print(f"\n🎤 Speak clearly... Press Ctrl+C to stop")
print(f"   VAD threshold : {SILENCE_THRESH} ({'disabled' if SILENCE_THRESH <= 0 else 'active'})")
print(f"   DEBUG_RMS     : {DEBUG_RMS}\n")

full_transcript = ""
last_partial    = ""

try:
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,        # smaller block = more responsive partial results
        dtype='int16',
        channels=1,
        callback=callback,
    ):
        while True:
            data = q.get()

            # ── VAD gate ──────────────────────────────────────────────────────
            chunk_rms = rms_from_bytes(data)
            if DEBUG_RMS:
                status = "transcribing..." if has_speech(data) else "SILENT, skipped"
                print(f"[DEBUG] RMS = {chunk_rms:.5f}  {status}")

            if not has_speech(data):
                continue

            # ── Feed to Vosk ──────────────────────────────────────────────────
            if rec.AcceptWaveform(data):
                # Final result for this utterance
                result = json.loads(rec.Result())
                text   = result.get("text", "").strip()

                # Clear the partial line
                if last_partial:
                    print(" " * (len(last_partial) + 5), end="\r")
                    last_partial = ""

                if text and not is_junk(text):
                    print(">>", text)
                    full_transcript += text + " "
                elif text and DEBUG_RMS:
                    print(f"   [filtered] '{text}'")

            else:
                # Partial result — show live feedback
                partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                if partial and partial != last_partial:
                    print(f"   ... {partial}", end="\r")
                    last_partial = partial

except KeyboardInterrupt:
    # Flush any remaining audio in the recognizer buffer
    final = json.loads(rec.FinalResult()).get("text", "").strip()
    if final and not is_junk(final):
        if last_partial:
            print(" " * (len(last_partial) + 5), end="\r")
        print(">>", final)
        full_transcript += final + " "
    print("\nRecording stopped.")

# ── Save transcript ────────────────────────────────────────────────────────────
prediction = full_transcript.strip()
timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
filename   = f"vosk_transcript_{timestamp}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(prediction)
print(f"Transcript saved to: {filename}")

# ── WER evaluation ─────────────────────────────────────────────────────────────
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
        print("\nCalibration tip: check [DEBUG] RMS values above.")
        print("Set SILENCE_THRESH to ~50% of your typical speech RMS.")
        print("Example: speech RMS ≈ 0.04 → set SILENCE_THRESH = 0.02")
elif not prediction:
    print("\n⚠  Empty transcript.")
    print("  • No [DEBUG] lines → mic not detected")
    print("  • [DEBUG] lines but no '>>' output → hallucination filter too strict")
    print("    or audio chunks too short for Vosk to finalize (try speaking longer)")
else:
    print("\nReference text not available. WER not calculated.")