from groq import Groq

from meetmind_ai.config.settings import GROQ_API_KEY


class Summarizer:
    """Meeting summarization using Groq API with LLaMA 3.1."""

    def __init__(self):
        self.client = None

        if not GROQ_API_KEY:
            print("[Summarizer] GROQ_API_KEY is missing in settings.")
            return

        try:
            self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as exc:
            print(f"[Summarizer] Failed to initialize Groq client: {exc}")

    def summarize(
        self,
        diarized_transcript_text: str,
        meeting_title: str = "",
        attendees: str = "",
    ) -> str:
        """Generate a structured meeting summary from a diarized transcript."""
        transcript = (diarized_transcript_text or "").strip()
        if not transcript:
            return "[Summarizer] Cannot summarize: transcript is empty."

        if self.client is None:
            return "[Summarizer] Cannot summarize: Groq client is not initialized. Check GROQ_API_KEY."

        system_prompt = (
            "You are an expert meeting summarizer. "
            "Extract key information and structure it clearly."
        )

        user_prompt = (
            f"Meeting Title: {meeting_title or 'Not provided'}\n"
            f"Attendees: {attendees or 'Not specified'}\n\n"
            "Diarized Transcript:\n"
            f"{transcript}\n\n"
            "Please provide only these two sections:\n"
            "1) Executive Summary\n"
            "2) Key Discussion Points\n\n"
            "Important rules:\n"
            "- Do not include title, duration, speaker count, decisions, action items, or next steps.\n"
            "- Do not invent commitments, owners, or deadlines not clearly present in transcript.\n"
            "- Keep output concise and factual."
        )

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            if not response.choices:
                return "[Summarizer] Groq API returned no choices in the response."

            message = response.choices[0].message
            content = (message.content or "").strip() if message else ""

            if not content:
                return "[Summarizer] Groq API returned an empty summary."

            return content
        except Exception as exc:
            error_text = str(exc)
            lowered = error_text.lower()

            if "rate limit" in lowered or "429" in lowered:
                return (
                    "[Summarizer] Rate limit reached while calling Groq API. "
                    "Please retry in a moment."
                )
            if "401" in lowered or "403" in lowered or "unauthorized" in lowered:
                return (
                    "[Summarizer] Authentication failed for Groq API. "
                    "Please verify GROQ_API_KEY."
                )

            return f"[Summarizer] Groq API error: {error_text}"
