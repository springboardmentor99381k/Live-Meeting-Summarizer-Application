import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    num_speakers: int = 2
    whisper_model: str = "base"
    language: str = "en"
    hf_token: str | None = None
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    output_dir: str = "output"

    def __post_init__(self) -> None:
        if self.hf_token is None:
            self.hf_token = os.getenv("HF_TOKEN")
        if self.groq_api_key is None:
            self.groq_api_key = os.getenv("GROQ_API_KEY")

    def validate(self) -> None:
        if not self.hf_token:
            raise ValueError("Missing HF_TOKEN in environment or .env file.")
        if not self.groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in environment or .env file.")
        if self.num_speakers < 1:
            raise ValueError("num_speakers must be at least 1.")
        if not self.whisper_model:
            raise ValueError("whisper_model is required.")
        if not self.language:
            raise ValueError("language is required.")
