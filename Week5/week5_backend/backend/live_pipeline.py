import whisper
from audio_recorder import record_audio
import librosa
import soundfile as sf

# -----------------------------
# 🎤 Resample Audio to 16kHz
# -----------------------------
def resample_audio(input_path, output_path="resampled.wav"):
    audio, sr = librosa.load(input_path, sr=16000)  # force 16kHz
    sf.write(output_path, audio, 16000)
    return output_path


# -----------------------------
# 🧠 Speech-to-Text
# -----------------------------
def speech_to_text(audio_file):
    print("\nRunning Speech-to-Text on LIVE audio...")

    model = whisper.load_model("base")

    result = model.transcribe(
        audio_file,
        language="en",          # ✅ force English
        temperature=0.0,        # ✅ avoid repetition
        no_speech_threshold=0.8
    )

    return result["text"]


# -----------------------------
# 👥 Speaker Segmentation (Simple)
# -----------------------------
def speaker_segmentation(text):
    print("\nRunning Speaker Segmentation...")

    sentences = text.split(".")
    speakers = ["Speaker 1", "Speaker 2"]

    speaker_text = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            speaker = speakers[i % 2]
            speaker_text.append(f"{speaker}: {sentence.strip()}")

    return speaker_text


# -----------------------------
# 📝 Smart Summary
# -----------------------------
def generate_summary(text):
    print("\nGenerating Smart Meeting Summary...")

    sentences = [s.strip() for s in text.split(".") if s.strip()]

    summary = "\n".join([f"- {s}" for s in sentences[:3]])

    action_items = "\n".join(
        [f"- Task {i+1}: {s}" for i, s in enumerate(sentences[:3])]
    )

    return summary, action_items


# -----------------------------
# 🚀 MAIN LIVE PIPELINE
# -----------------------------
def run_live_pipeline():
    print("\nStarting LIVE backend pipeline...\n")

    # 🎤 Step 1: Record Audio
    record_audio()

    print("Audio recording saved successfully.")

    # 🔄 Step 2: Resample to 16kHz
    audio_file = resample_audio("recorded_meeting.wav")

    # 🧠 Step 3: Speech-to-Text
    transcript = speech_to_text(audio_file)

    print("\nRaw Transcript:\n", transcript)

    # 👥 Step 4: Speaker Segmentation
    speaker_output = speaker_segmentation(transcript)

    print("\nSpeaker-wise Transcript:\n")
    for line in speaker_output:
        print(line)

    # 📝 Step 5: Summary + Action Items
    summary, actions = generate_summary(transcript)

    final_output = f"""
Final Meeting Output:

Meeting Summary:
{summary}

Action Items:
{actions}
"""

    print(final_output)

    # 💾 Save output
    with open("live_summary.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

    print("\nSaved to live_summary.txt")