"""GapGuard AI - RAG package (Member 1).

Contract functions:
    ingest_requirements(pdf_path) -> int
    retrieve(query, category=None, k=3) -> list[Evidence]
"""
from rag.ingest import ingest_requirements  # noqa: F401
from rag.retriever import (  # noqa: F401
    get_all_chunks,
    get_requirements_text,
    retrieve,
    retrieve_chunks,
)
