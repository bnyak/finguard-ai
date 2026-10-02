from pathlib import Path
import pymupdf

def extract_pages(pdf_path: Path) -> list[dict]:
    """Extract text and page metadata from a PDF document."""

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.suffix}")

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages

