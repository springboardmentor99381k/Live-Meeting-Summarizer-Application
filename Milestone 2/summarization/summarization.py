from transformers import pipeline
import re
from collections import defaultdict

# -----------------------------
# Load summarization model
# -----------------------------
print("Loading summarization model...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# -----------------------------
# Load transcript
# -----------------------------
with open("Diarization/diarization_output.txt", "r", encoding="utf-8") as f:
    transcript = f.readlines()

print("Transcript lines loaded:", len(transcript))

# -----------------------------
# Clean transcript
# -----------------------------
irrelevant_keywords = [
    "animal","monkey","bigo","beagle","family",
    "uh","um","okay","yes","no","haha","lol"
]

clean_lines = []

for line in transcript:

    line = re.sub(r"\[.*?\]", "", line)
    line = re.sub(r"(SPEAKER_\d+:)+", "", line)
    line = re.sub(r"\d+\.\d+\s*-\s*\d+\.\d+", "", line)

    line = re.sub(r'\b(\w+)( \1\b)+', r'\1', line)
    line = re.sub(r"\s+", " ", line).strip()

    if len(line.split()) > 7 and not any(word in line.lower() for word in irrelevant_keywords):
        clean_lines.append(line)

clean_text = " ".join(clean_lines)

print("Clean transcript length:", len(clean_text))

# -----------------------------
# Speaker Contributions
# -----------------------------
print("\nSpeaker Contributions:\n")

speaker_words = defaultdict(int)
current_speaker = None

for line in transcript:

    line = line.strip()

    match = re.search(r"(SPEAKER_\d+|Unknown)", line)

    if match:
        current_speaker = match.group(1)
        continue

    if current_speaker and line != "":
        speaker_words[current_speaker] += len(line.split())

total_words = sum(speaker_words.values())

if total_words == 0:
    total_words = 1

for speaker, words in speaker_words.items():
    percent = (words / total_words) * 100
    print(f"{speaker} : {percent:.2f}%")

# -----------------------------
# Meeting Analytics
# -----------------------------
total_speakers = len(speaker_words)
most_active_speaker = max(speaker_words, key=speaker_words.get)

print("\nMeeting Analytics:\n")
print("Total Speakers:", total_speakers)
print("Total Transcript Lines:", len(transcript))
print("Total Words Spoken:", total_words)
print("Most Active Speaker:", most_active_speaker)

# -----------------------------
# Chunk transcript
# -----------------------------
chunks = []
temp = ""

for line in clean_lines:

    temp += " " + line

    if len(temp.split()) > 120:
        chunks.append(temp.strip())
        temp = ""

if temp.strip():
    chunks.append(temp.strip())

print("Total chunks created:", len(chunks))

# -----------------------------
# Generate summary
# -----------------------------
final_summary = ""

for chunk in chunks:

    prompt = f"""
Summarize the following meeting transcript into short professional sentences.
Focus only on the main discussion points.

Transcript:
{chunk}
"""

    result = summarizer(
        prompt,
        max_length=120,
        min_length=40,
        do_sample=False
    )

    final_summary += result[0]["summary_text"].strip() + "\n"

# -----------------------------
# Print Report
# -----------------------------
print("\n===== AI MEETING REPORT =====\n")

print("Meeting Title:")
print("Project Discussion Meeting\n")

print("Main Discussion Points:\n")
print(final_summary)

print("Speaker Contributions:\n")

for speaker, words in speaker_words.items():
    percent = (words / total_words) * 100
    print(f"{speaker} : {percent:.2f}%")

print("\nMeeting Analytics:\n")

print("Total Speakers:", total_speakers)
print("Total Transcript Lines:", len(transcript))
print("Total Words Spoken:", total_words)
print("Most Active Speaker:", most_active_speaker)

# -----------------------------
# Save Report
# -----------------------------
with open("summarization/summary.txt", "w", encoding="utf-8") as f:

    f.write("===== AI MEETING REPORT =====\n\n")

    f.write("Meeting Title:\n")
    f.write("Project Discussion Meeting\n\n")

    f.write("Main Discussion Points:\n")
    f.write(final_summary + "\n")

    f.write("Speaker Contributions:\n")

    for speaker, words in speaker_words.items():
        percent = (words / total_words) * 100
        f.write(f"{speaker} : {percent:.2f}%\n")

    f.write("\nMeeting Analytics:\n")

    f.write(f"Total Speakers: {total_speakers}\n")
    f.write(f"Total Transcript Lines: {len(transcript)}\n")
    f.write(f"Total Words Spoken: {total_words}\n")
    f.write(f"Most Active Speaker: {most_active_speaker}\n")

print("\nSummary saved to summary.txt")