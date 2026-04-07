from fpdf import FPDF
from datetime import datetime
import re


def build_markdown(title, transcript, diarized_transcript, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# {title}

**Generated on:** {timestamp}

## Summary
{summary}

## Diarized Transcript
{diarized_transcript}

## Full Transcript
{transcript}
"""
    return content


def save_markdown_file(content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def _clean_pdf_text(text):
    if not text:
        return ""

    text = str(text)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    text = text.replace("\t", "    ")
    text = re.sub(r"(\S{80})(?=\S)", r"\1 ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def save_pdf_file(title, transcript, diarized_transcript, summary, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    left_margin = 10
    right_margin = 10
    pdf.set_left_margin(left_margin)
    pdf.set_right_margin(right_margin)
    pdf.set_x(left_margin)

    usable_width = pdf.w - left_margin - right_margin

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(usable_width, 10, _clean_pdf_text(title))

    pdf.ln(4)

    sections = [
        ("Summary", summary),
        ("Diarized Transcript", diarized_transcript),
        ("Full Transcript", transcript),
    ]

    for heading, body in sections:
        pdf.set_font("Arial", "B", 13)
        pdf.set_x(left_margin)
        pdf.multi_cell(usable_width, 10, _clean_pdf_text(heading))

        pdf.set_font("Arial", size=11)
        pdf.set_x(left_margin)
        pdf.multi_cell(usable_width, 8, _clean_pdf_text(body))
        pdf.ln(3)

    pdf.output(output_path)