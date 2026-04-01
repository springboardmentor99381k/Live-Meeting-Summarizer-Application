import whisper
from pyannote.audio import Pipeline
from transformers import pipeline
from pydub import AudioSegment

# -----------------------------
# Load Models
# -----------------------------
print("Loading models...")

whisper_model = whisper.load_model("base")

diarization_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token="your token here"
)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

print("Models loaded successfully")

# -----------------------------
# Trim Audio
# -----------------------------
def trim_audio(input_audio, output_audio, duration_seconds=120):

    print("Trimming audio to 2 minutes...")

    audio = AudioSegment.from_file(input_audio)

    trimmed_audio = audio[:duration_seconds * 1000]

    trimmed_audio.export(output_audio, format="wav")

    print("Trimmed audio saved at:", output_audio)

    return output_audio


# -----------------------------
# Speech To Text
# -----------------------------
def speech_to_text(audio_file):

    print("Running Speech-to-Text...")

    result = whisper_model.transcribe(audio_file)

    return result["segments"]


# -----------------------------
# Speaker Diarization
# -----------------------------
def speaker_diarization(audio_file):

    print("Running Speaker Diarization...")

    diarization = diarization_pipeline(audio_file)

    speakers = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):

        speakers.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return speakers


# -----------------------------
# Merge Transcript + Speakers
# -----------------------------
def merge_transcript_and_speakers(transcript, speakers):

    print("Merging transcript with speaker labels...")

    merged_text = []

    for segment in transcript:

        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        speaker_label = "Unknown"

        for sp in speakers:

            if (start >= sp["start"] and start <= sp["end"]) or \
               (end >= sp["start"] and end <= sp["end"]):

                speaker_label = sp["speaker"]
                break

        merged_text.append(f"{speaker_label}: {text}")

    return "\n".join(merged_text)


# -----------------------------
# Clean Transcript for Summary
# -----------------------------
def clean_transcript(text):

    lines = text.split("\n")

    cleaned_lines = []

    for line in lines:

        if ":" in line:
            cleaned_lines.append(line.split(":",1)[1].strip())
        else:
            cleaned_lines.append(line.strip())

    return " ".join(cleaned_lines)


# -----------------------------
# Generate Summary
# -----------------------------
def generate_summary(text):

    print("Generating meeting summary...")

    max_chunk = 900
    chunks = []

    for i in range(0, len(text), max_chunk):
        chunks.append(text[i:i+max_chunk])

    final_summary = ""

    for chunk in chunks:

        summary = summarizer(
            chunk,
            max_length=100,
            min_length=40,
            do_sample=False
        )

        final_summary += summary[0]["summary_text"] + " "

    return final_summary.strip()


# -----------------------------
# Extract Action Items
# -----------------------------
def extract_action_items(text):

    print("Extracting action items...")

    keywords = ["should", "must", "need to", "action", "task", "follow up"]

    sentences = text.split(".")

    actions = []

    for sentence in sentences:

        for word in keywords:

            if word in sentence.lower():
                actions.append(sentence.strip())

    if not actions:
        return ["No action items detected."]

    return actions


# -----------------------------
# Complete Pipeline
# -----------------------------
def process_meeting(audio_file):

    trimmed_audio = trim_audio(audio_file, "milestone3/trimmed_meeting.wav")

    transcript = speech_to_text(trimmed_audio)

    speakers = speaker_diarization(trimmed_audio)

    merged_text = merge_transcript_and_speakers(transcript, speakers)

    clean_text = clean_transcript(merged_text)

    summary = generate_summary(clean_text)

    actions = extract_action_items(clean_text)

    return merged_text, summary, actions


# -----------------------------
# Main
# -----------------------------
def main():

    audio_file = "Data/sample.wav"

    transcript, summary, actions = process_meeting(audio_file)

    print("\n==============================")
    print("DIARIZED TRANSCRIPT")
    print("==============================\n")

    print(transcript)

    print("\n==============================")
    print("MEETING SUMMARY")
    print("==============================\n")

    print(summary)

    print("\n==============================")
    print("ACTION ITEMS")
    print("==============================\n")

    for action in actions:
        print("-", action)


if __name__ == "__main__":
    main()