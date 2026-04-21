class PDFParser:
    def parse(self, path: str) -> str:
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t: parts.append(t)
            return "\n".join(parts)
        except ImportError:
            return "[PDFParser] install pdfplumber"
        except Exception as e:
            return f"[PDFParser error] {e}"
