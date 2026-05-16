# Extracts raw text from uploaded PDF or TXT files

import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    Falls back to pdfminer if PyPDF2 returns empty text.

    Args:
        file_bytes: Raw bytes of the PDF file

    Returns:
        Extracted text as a string
    """
    text = ""

    # --- Method 1: PyPDF2 ---
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        logger.warning(f"PyPDF2 failed: {e}")

    # --- Method 2: pdfminer fallback ---
    if not text.strip():
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(io.BytesIO(file_bytes))
        except Exception as e:
            logger.warning(f"pdfminer also failed: {e}")

    return text.strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decode a plain text file.

    Args:
        file_bytes: Raw bytes of the TXT file

    Returns:
        Decoded text string
    """
    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1").strip()


def extract_text(uploaded_file) -> str:
    """
    Main entry point. Detects file type and routes to the correct extractor.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Raw extracted text string, or empty string on failure
    """
    if uploaded_file is None:
        return ""

    file_bytes = uploaded_file.read()
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".txt"):
        text = extract_text_from_txt(file_bytes)
    else:
        # Try TXT decoding as a last resort
        text = extract_text_from_txt(file_bytes)

    if not text.strip():
        raise ValueError(
            f"Could not extract any text from '{uploaded_file.name}'. "
            "Make sure the PDF is not scanned/image-only."
        )

    return text
