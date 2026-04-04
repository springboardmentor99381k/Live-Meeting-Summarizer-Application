import os
from groq import Groq

def summarize(text: str) -> str:
    """
    Summarize the diarized transcript using Groq LLM.
    Returns a fallback message if API key is missing or API call fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Summary unavailable. API key not set."

    try:
        client = Groq(api_key=api_key)
        prompt = f"Summarize the following meeting transcript concisely:\n\n{text}"
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary unavailable. Error: {str(e)}"