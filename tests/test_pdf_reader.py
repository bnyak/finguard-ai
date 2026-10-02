from pathlib import Path
import pymupdf
import pytest
from finguard.ingestion.pdf_reader import extract_pages

def test_extract_pages_returns_text_and_page_numbers(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"

    document = pymupdf.open()

    page_one = document.new_page()
    page_one.insert_text((72, 72), "FinGuard policy page one.")

    page_two = document.new_page()
    page_two.insert_text((72, 72), "Enhanced review is required.")

    document.save(pdf_path)
    document.close()

    pages = extract_pages(pdf_path)

    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert "FinGuard policy page one." in pages[0]["text"]
    assert "Enhanced review is required." in pages[1]["text"]

def test_extract_pages_raises_error_when_file_does_not_exist(tmp_path: Path) -> None:
    missing_pdf = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_pages(missing_pdf)


def test_extract_pages_rejects_non_pdf_file(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("This is not a PDF.")

    with pytest.raises(ValueError):
        extract_pages(text_file)