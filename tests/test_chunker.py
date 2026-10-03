import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag._sample_data import SAMPLE_PAGES
from rag.chunker import chunk_pages, classify_category, normalize_pages


def _by_section(chunks):
    return {c.section: c for c in chunks}


def test_sections_detected_with_numbers_and_titles():
    chunks = chunk_pages(SAMPLE_PAGES, source="Scholarship Requirements")
    sections = {c.section for c in chunks}
    assert "Section 4: Recommendation Letter" in sections
    assert "Section 3: Required Documents" in sections
    assert "Section 7: Deadlines" in sections


def test_page_numbers_are_correct():
    s = _by_section(chunk_pages(SAMPLE_PAGES, source="X"))
    assert s["Section 2: Eligibility Criteria"].page == 1
    assert s["Section 4: Recommendation Letter"].page == 2
    assert s["Section 7: Deadlines"].page == 3


def test_categories():
    s = _by_section(chunk_pages(SAMPLE_PAGES, source="X"))
    assert s["Section 3: Required Documents"].category == "documents"
    assert s["Section 4: Recommendation Letter"].category == "documents"
    assert s["Section 2: Eligibility Criteria"].category == "eligibility"
    assert s["Section 6: Financial Information"].category == "financial"
    assert s["Section 7: Deadlines"].category == "deadline"


def test_bullets_are_not_headings():
    pages = ["Section 1: Docs\n- 1. CNIC\n- 2. CV\n(a) Photo\n"]
    chunks = chunk_pages(pages, source="X")
    assert len(chunks) == 1
    assert chunks[0].section == "Section 1: Docs"
    assert "CNIC" in chunks[0].text and "Photo" in chunks[0].text


def test_numbered_caps_heading():
    chunks = chunk_pages(["4. REQUIRED DOCUMENTS\n- CV\n- CNIC"], source="X")
    assert chunks[0].section == "Section 4: Required Documents"
    assert chunks[0].section_number == "4"


def test_no_headings_falls_back_to_page_labels():
    chunks = chunk_pages(["just some text about things", "more text here"], source="X")
    assert [c.section for c in chunks] == ["Page 1", "Page 2"]


def test_max_chars_respected_and_no_text_lost():
    long_text = "Section 1: Big\n" + " ".join(f"Sentence number {i} is here." for i in range(200))
    chunks = chunk_pages([long_text], source="X", max_chars=300)
    assert len(chunks) > 3
    assert all(len(c.text) <= 300 for c in chunks)
    assert "Sentence number 199 is here." in " ".join(c.text for c in chunks)


def test_metadata_complete_and_chroma_safe():
    for c in chunk_pages(SAMPLE_PAGES, source="X"):
        md = c.to_metadata()
        for key in ("text", "source", "section", "page", "category", "chunk_index"):
            assert key in md
        assert all(isinstance(v, (str, int, float, bool)) for v in md.values())


def test_unique_ids():
    chunks = chunk_pages(SAMPLE_PAGES, source="X")
    assert len({c.id for c in chunks}) == len(chunks)


def test_normalize_pages_accepts_many_shapes():
    class P:
        page, text = 7, "hello"

    assert normalize_pages(["a"]) == [(1, "a")]
    assert normalize_pages([(2, "b")]) == [(2, "b")]
    assert normalize_pages([("c", 3)]) == [(3, "c")]
    assert normalize_pages([{"page": 4, "text": "d"}]) == [(4, "d")]
    assert normalize_pages([P()]) == [(7, "hello")]


def test_classify_category_general_fallback():
    assert classify_category("", "lorem ipsum dolor") == "general"
