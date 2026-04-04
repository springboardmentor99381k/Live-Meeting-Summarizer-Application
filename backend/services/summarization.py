from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_TOKEN = os.getenv("GEMINI_TOKEN")

# genai.configure(api_key=GOOGLE_API_TOKEN)
client = genai.Client(api_key=GOOGLE_API_TOKEN)

# model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")


def summarize(text: str):
    prompt = f"""
    You are a meeting assistant

    Summarize the following conversation clearly
    
    Include:
    - Key discussion points
    - Important decisions
    - Action items

    Transcript:
    {text}
    """
    
    response = client.models.generate_content(
        model = "gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    # print(response.text)
    return response.text
    