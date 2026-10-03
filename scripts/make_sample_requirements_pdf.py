"""Generate a 3-page sample requirements PDF for local RAG testing.

    python scripts/make_sample_requirements_pdf.py

Output: data/requirements/sample_scholarship_requirements.pdf
(Member 6 owns the official demo PDF; this one is just so you can test immediately.)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz

from rag._sample_data import SAMPLE_PAGES

OUT = ROOT / "data" / "requirements" / "sample_scholarship_requirements.pdf"


def main() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for text in SAMPLE_PAGES:
        page = doc.new_page(width=595, height=842)  # A4
        rect = fitz.Rect(56, 56, 539, 786)
        # unwrap hard-wrapped lines inside bullets/paragraphs so the PDF re-wraps naturally
        leftover = page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        if leftover < 0:
            raise RuntimeError("Text did not fit on the page; shorten SAMPLE_PAGES.")
    doc.save(OUT)
    doc.close()
    print(f"Wrote {OUT}")
    return OUT


if __name__ == "__main__":
    main()
