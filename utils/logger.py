from datetime import datetime
import json
import os
import pandas as pd


def save_session_logs(title, transcript, diarized_transcript, summary, output_dir="outputs/logs"):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    session_data = {
        "title": title,
        "timestamp": timestamp,
        "transcript": transcript,
        "diarized_transcript": diarized_transcript,
        "summary": summary
    }

    json_path = os.path.join(output_dir, f"session_{timestamp}.json")
    parquet_path = os.path.join(output_dir, f"session_{timestamp}.parquet")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame([session_data])
    df.to_parquet(parquet_path, index=False)

    return json_path, parquet_path