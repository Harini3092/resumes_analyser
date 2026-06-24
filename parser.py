import pdfplumber
from docx import Document


def extract_text(filepath):

    text = ""

    if filepath.endswith(".pdf"):

        with pdfplumber.open(filepath) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:

                    text += page_text

    elif filepath.endswith(".docx"):

        doc = Document(filepath)

        for para in doc.paragraphs:

            text += para.text + "\n"

    return text.lower()