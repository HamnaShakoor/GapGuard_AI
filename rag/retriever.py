"""Metadata-aware retrieval for GapGuard AI.

Public API (agreed contract):
    retrieve(query, category=None, k=3) -> list[Evidence]

Extra helpers for teammates:
    retrieve_chunks(...)         -> list[RetrievedChunk]  (adds score/category/source)
    get_all_chunks()             -> every requirement chunk in document order
    get_requirements_text()      -> whole requirements doc as one string (for Member 3's
                                    requirement_agent to extract the structured checklist)

Categories: documents | eligibility | deadline | financial | academic | general
`category` may be a string, a list of strings, or None (no filter).
If the category filter returns nothing, we automatically fall back to unfiltered search.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Union

from rag import vectorstore

try:  # use the team's shared contract when it exists
    from schemas import Evidence  # type: ignore
except ImportError:  # standalone fallback so this module works before schemas.py lands
    from pydantic import BaseModel

    class Evidence(BaseModel):  # type: ignore[no-redef]
        text: str
        section: str
        page: int


Category = Union[str, Sequence[str], None]


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    section: str
    page: int
    page_end: int
    category: str
    source: str
    score: Optional[float] = None  # cosine similarity (1.0 = identical); None for get_all

    def to_evidence(self) -> Evidence:
        return Evidence(text=self.text, section=self.section, page=self.page)


def _to_chunk(row: dict, score: Optional[float] = None) -> RetrievedChunk:
    m = row["metadata"]
    return RetrievedChunk(
        chunk_id=row["id"], text=m["text"], section=m["section"], page=int(m["page"]),
        page_end=int(m.get("page_end", m["page"])), category=m.get("category", "general"),
        source=m.get("source", ""), score=score,
    )


def _build_where(category: Category) -> Optional[dict]:
    if category is None:
        return None
    if isinstance(category, str):
        cats = [category.strip().lower()]
    else:
        cats = [c.strip().lower() for c in category]
    cats = [c for c in cats if c and c != "all"]
    if not cats:
        return None
    return {"category": cats[0]} if len(cats) == 1 else {"category": {"$in": cats}}


def retrieve_chunks(
    query: str,
    category: Category = None,
    k: int = 3,
    min_score: Optional[float] = None,
    strict: bool = False,
) -> list[RetrievedChunk]:
    """Similarity search, optionally restricted by metadata category.

    strict=False -> if the filter yields no hits, retry without the filter.
    min_score    -> drop results below this cosine similarity.
    """
    where = _build_where(category)
    rows = vectorstore.query(query, k=k, where=where)
    if not rows and where is not None and not strict:
        rows = vectorstore.query(query, k=k, where=None)
    results = [_to_chunk(r, score=round(1.0 - r["distance"], 4)) for r in rows]
    if min_score is not None:
        results = [r for r in results if r.score is not None and r.score >= min_score]
    return results


def retrieve(query: str, category: Category = None, k: int = 3) -> list[Evidence]:
    """Contract function: returns Evidence(text, section, page) best-first."""
    return [c.to_evidence() for c in retrieve_chunks(query, category, k)]


def get_all_chunks(category: Category = None) -> list[RetrievedChunk]:
    return [_to_chunk(r) for r in vectorstore.get_all(_build_where(category))]


def get_requirements_text() -> str:
    """Whole requirements document with section/page markers, in reading order."""
    parts: list[str] = []
    last_section = None
    for c in get_all_chunks():
        if c.section != last_section:
            parts.append(f"\n[{c.section} | page {c.page}]")
            last_section = c.section
        parts.append(c.text)
    return "\n".join(parts).strip()
