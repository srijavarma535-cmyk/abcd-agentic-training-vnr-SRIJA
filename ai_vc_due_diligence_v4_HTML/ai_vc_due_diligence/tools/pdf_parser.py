"""
PDF Parser Tool
Extracts text from pitch deck PDFs.
"""
from config.settings import Settings

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


class PDFParser:
    def __init__(self, settings: Settings):
        self.settings = settings

    def parse(self, path: str) -> str:
        """Extract text from a PDF file."""
        if not HAS_PDF:
            return "[PDFParser] pdfplumber not installed. Run: pip install pdfplumber"

        try:
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts)
        except Exception as e:
            return f"[PDFParser] Could not parse {path}: {e}"
