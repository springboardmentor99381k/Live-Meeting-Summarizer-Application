from module3.diarization_engine import DiarizationEngine
from llm_pipeline import run_llm_pipeline


def main():
    print("Starting AI Meeting Pipeline...")

    # Step 1: Diarization
    engine = DiarizationEngine()

    input_audio = "recordings\IS1009a-Headset.wav"
    output_file = "results/transcripts.txt"

    print("Running diarization...")
    engine.process(input_audio, output_file)

    print("Diarization completed.")

    # Step 2: LLM Summarization + Evaluation
    run_llm_pipeline(meeting_type="general")

    print("Full pipeline completed successfully.")


if __name__ == "__main__":
    main()
