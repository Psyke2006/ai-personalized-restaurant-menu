import io
from typing import Tuple
import pymupdf

SUPPORTED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg"]

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extracts text from PDF using PyMuPDF.
    Handles image files gracefully.
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = ""
        try:
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        return text.strip()

    elif any(filename_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
        # Try PyMuPDF page-based or OCR extraction if available
        try:
            doc = pymupdf.open(stream=file_bytes, filetype=filename_lower.split(".")[-1])
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception:
            return ""

    else:
        raise ValueError(f"Unsupported file format: {filename}")
