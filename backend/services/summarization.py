from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_TOKEN = os.getenv("GEMINI_TOKEN")

client = None
if GOOGLE_API_TOKEN:
    try:
        client = genai.Client(api_key=GOOGLE_API_TOKEN)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")

def summarize(text: str):
    if not client:
        return "⚠️ **API Key Missing**: Please provide your `GEMINI_TOKEN` in the `backend/.env` file to unlock full AI Meeting Summarization capabilities. Your transcript has still been successfully captured below!"
        
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
    
    try:
        response = client.models.generate_content(
            model = "gemini-3.1-flash-lite-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Summarization error: {e}")
        return f"⚠️ **AI Summarization Failed**: Error communicating with Gemini API. Error details: {e}"