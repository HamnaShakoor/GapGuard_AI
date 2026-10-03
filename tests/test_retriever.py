import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag import ingest, retriever, vectorstore
from rag._sample_data import SAMPLE_PAGES


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Isolated Chroma dir + offline embeddings, so tests need no network."""
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CHROMA_COLLECTION", "test_requirements")
    monkeypatch.setenv("EMBEDDING_BACKEND", "hash")
    ingest.ingest_pages(SAMPLE_PAGES, source_name="Scholarship Requirements")
    return tmp_path


def test_ingest_returns_chunk_count(store):
    assert vectorstore.collection_count() >= 8


def test_recommendation_letter_retrieves_section_4_page_2(store):
    ev = retriever.retrieve("recommendation letter academic referee", "documents", k=3)
    assert ev[0].section == "Section 4: Recommendation Letter"
    assert ev[0].page == 2
    assert "academic referee" in ev[0].text


def test_deadline_query(store):
    ev = retriever.retrieve("when is the application deadline", "deadline", k=2)
    assert ev[0].section == "Section 7: Deadlines"
    assert ev[0].page == 3


def test_category_filter_is_respected(store):
    chunks = retriever.retrieve_chunks("income", "financial", k=5)
    assert chunks and all(c.category == "financial" for c in chunks)


def test_multiple_categories(store):
    chunks = retriever.retrieve_chunks("deadline or income", ["deadline", "financial"], k=10)
    assert {c.category for c in chunks} <= {"deadline", "financial"}


def test_unknown_category_falls_back_to_unfiltered(store):
    assert retriever.retrieve("deadline", "nonexistent-category", k=2)


def test_strict_mode_returns_empty_for_unknown_category(store):
    assert retriever.retrieve_chunks("deadline", "nonexistent-category", strict=True) == []


def test_reset_replaces_previous_requirements(store):
    ingest.ingest_pages(["Section 1: Only Thing\n- A single new rule."], source_name="Other")
    assert vectorstore.collection_count() == 1
    assert retriever.retrieve("rule", k=3)[0].section == "Section 1: Only Thing"


def test_get_requirements_text_keeps_order_and_markers(store):
    text = retriever.get_requirements_text()
    assert text.index("Section 3") < text.index("Section 7")
    assert "page 2" in text


def test_txt_ingest_via_bytes(tmp_path, monkeypatch):
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "c2"))
    monkeypatch.setenv("EMBEDDING_BACKEND", "hash")
    n = ingest.ingest_requirements(
        b"Section 1: Documents\n- CV is mandatory for every applicant.\n", filename="reqs.txt"
    )
    assert n == 1


def test_empty_file_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("CHROMA_DIR", str(tmp_path / "c3"))
    with pytest.raises(ValueError):
        ingest.ingest_requirements(b"  ", filename="empty.txt")
