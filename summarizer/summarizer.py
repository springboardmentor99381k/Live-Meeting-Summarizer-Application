# from transformers import pipeline
# from .prompts import general_meeting_prompt


# class MeetingSummarizer:

#     def __init__(self, model_name="google/flan-t5-base"):

#         print("Loading summarization model...")

#         self.summarizer = pipeline(
#             "text-generation",
#             model=model_name
#         )

#     def summarize(self, transcript):

#         prompt = general_meeting_prompt(transcript)

#         result = self.summarizer(
#             prompt,
#             max_length=200,
#             do_sample=False
#         )

#         return result[0]["generated_text"]
# from transformers import pipeline
# from .prompts import general_meeting_prompt


# class MeetingSummarizer:

#     def __init__(self, model_name="google/flan-t5-base"):

#         print("Loading summarization model...")

#         # Use text2text pipeline for T5 models
#         self.summarizer = pipeline(
#             "text2text-generation",
#             model=model_name
#         )

#     def summarize(self, transcript):

#         # Add summarization instruction
#         prompt = "Summarize the following meeting transcript:\n\n" + transcript

#         result = self.summarizer(
#             prompt,
#             max_length=150,
#             min_length=40,
#             do_sample=False
#         )

#         return result[0]["generated_text"]

# from transformers import pipeline


# class MeetingSummarizer:

#     def __init__(self, model_name="gpt2"):

#         print("Loading summarization model...")

#         self.summarizer = pipeline(
#             "text-generation",
#             model=model_name
#         )

#     def summarize(self, transcript):

#         prompt = f"""
# Summarize the following meeting transcript in 4-5 sentences.

# Transcript:
# {transcript}

# Summary:
# """

#         result = self.summarizer(
#             prompt,
#             max_length=180,
#             num_return_sequences=1,
#             truncation=True
#         )

#         generated_text = result[0]["generated_text"]

#         # remove prompt part to keep only summary
#         summary = generated_text.replace(prompt, "").strip()

#         return summary
# from transformers import pipeline


# class MeetingSummarizer:

#     def __init__(self):

#         print("Loading summarization model...")

#         # Load BART summarization model
#         self.summarizer = pipeline(
#             "summarization",
#             model="facebook/bart-large-cnn"
#         )

#     def summarize(self, transcript):

#         summary = self.summarizer(
#             transcript,
#             max_length=130,
#             min_length=40,
#             do_sample=False
#         )

#         return summary[0]["summary_text"]
from transformers import pipeline


class MeetingSummarizer:

    def __init__(self):

        print("Loading summarization model...")

        # Load BART summarization model
        self.summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )

    def summarize(self, transcript):

        summary = self.summarizer(
            transcript,
            max_length=100,
            min_length=30,
            do_sample=False
        )

        return summary[0]["summary_text"]