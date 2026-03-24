def load_transcript(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    return transcript