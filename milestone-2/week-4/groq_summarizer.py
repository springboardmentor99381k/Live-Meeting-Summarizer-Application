import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqSummarizer:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("MODEL_NAME", "llama3-70b-8192")
        self.client = Groq(api_key=self.api_key)

    def summarize(self, transcript):

        prompt = f"""
You are an AI meeting assistant.

Provide:
1. Meeting Overview
2. Key Discussion Points
3. Decisions Made
4. Action Items (with speaker names if possible)

Transcript:
{transcript}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert meeting summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        return response.choices[0].message.content
