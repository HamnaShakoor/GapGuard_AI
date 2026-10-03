"""Section-aware chunking with metadata for GapGuard AI.

Pipeline:  pages -> sections (by heading detection) -> units (bullets/paragraphs)
           -> packed chunks (<= max_chars) -> metadata (section, page, category)

Why section-aware?  A recommendation-letter rule lives in "Section 4".  If we
chunked blindly every N characters, the rule could be cut in half and we could
not cite "Section 4, page 2" as evidence.

Heading conventions detected (see rag/_sample_data.py):
    "Section 4: Required Documents"   /  "Part 2 - Eligibility"
    "4. REQUIRED DOCUMENTS"           (numbered, ALL CAPS)
    "## Required Documents"           (markdown-style, also produced for DOCX headings)
List items ("- ...", "(a) ...", "1. ...") are NOT headings (except numbered ALL-CAPS lines).
If no headings are found at all, chunks are labelled "Page N".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

MAX_CHARS = 900

CATEGORIES = ["documents", "eligibility", "deadline", "financial", "academic", "general"]


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Chunk:
    id: str
    text: str            # raw chunk text (this is what we show as evidence)
    source: str          # e.g. "National Ai Excellence Scholarship 2026"
    section: str         # e.g. "Section 4: Recommendation Letter"
    section_number: str  # e.g. "4" ("" if none)
    section_title: str   # e.g. "Recommendation Letter"
    page: int            # first page of the chunk (1-based)
    page_end: int
    category: str        # documents | eligibility | deadline | financial | academic | general
    chunk_index: int

    @property
    def embed_text(self) -> str:
        """Text that is embedded: the section label gives the chunk context."""
        return f"{self.section}\n{self.text}"

    def to_metadata(self) -> dict[str, Any]:
        """Chroma metadata (only str/int/float/bool allowed)."""
        return {
            "text": self.text,
            "source": self.source,
            "section": self.section,
            "section_number": self.section_number,
            "section_title": self.section_title,
            "page": self.page,
            "page_end": self.page_end,
            "category": self.category,
            "chunk_index": self.chunk_index,
        }


# --------------------------------------------------------------------------- #
# Page normalisation (accepts whatever Member 2's pdf_reader returns)
# --------------------------------------------------------------------------- #
def normalize_pages(pages: Iterable[Any]) -> list[tuple[int, str]]:
    """Accept str | (page, text) | (text, page) | dict | object(.page,.text)."""
    out: list[tuple[int, str]] = []
    for i, p in enumerate(pages, start=1):
        if isinstance(p, str):
            page_no, text = i, p
        elif isinstance(p, (tuple, list)) and len(p) == 2:
            a, b = p
            page_no, text = (a, b) if isinstance(a, int) else (b, a)
        elif isinstance(p, dict):
            page_no, text = p.get("page", p.get("page_number", i)), p.get("text", "")
        else:
            page_no = getattr(p, "page", getattr(p, "page_number", i))
            text = getattr(p, "text", "")
        out.append((int(page_no), text or ""))
    return out


# --------------------------------------------------------------------------- #
# Heading detection
# --------------------------------------------------------------------------- #
_ACRONYMS = {"CNIC", "CV", "GPA", "CGPA", "HEC", "PDF", "AI", "FAQ", "PKR", "USD", "BS", "MS", "PHD"}

_HEADING_RES = [
    re.compile(r"^(?:section|part|article)\s+(\d+(?:\.\d+)*)\s*[:.\-–—]\s*(.+?)\s*$", re.I),
    re.compile(r"^(\d+(?:\.\d+)*)[.)]\s+([A-Z][A-Z0-9 &/,\-()']{4,})$"),  # "4. REQUIRED DOCUMENTS"
]
_MD_HEADING = re.compile(r"^#{1,4}\s+(.+?)\s*$")
_BULLET = re.compile(r"^(?:[-•*–·▪]|\(?[A-Za-z0-9]{1,2}[.)])\s+")


def _pretty_title(title: str) -> str:
    title = title.strip().rstrip(":").strip()
    if title.isupper():
        return " ".join(w if w in _ACRONYMS else w.capitalize() for w in title.split())
    return title


def _match_heading(line: str) -> tuple[str, str] | None:
    """Return (number, title) if the line is a heading, else None."""
    if len(line) > 100:
        return None
    for rx in _HEADING_RES:
        m = rx.match(line)
        if m:
            return m.group(1), _pretty_title(m.group(2))
    m = _MD_HEADING.match(line)
    if m:
        return "", _pretty_title(m.group(1))
    return None


# --------------------------------------------------------------------------- #
# Category classification (metadata for filtered retrieval)
# --------------------------------------------------------------------------- #
_MONTHS = r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b"

_CATEGORY_PATTERNS: dict[str, list[str]] = {
    "documents": [
        r"\bdocuments?\b", r"\bsubmi", r"\battach", r"\bupload", r"\bcertificate", r"\bletter",
        r"\bcnic\b", r"\bphotograph", r"\bpassport", r"\bcv\b", r"\bresume\b", r"\btranscript",
        r"\benclos", r"\bchecklist", r"\bstatement\b", r"\bproof\b", r"\breferee",
    ],
    "eligibility": [
        r"\beligib", r"\bcriteri", r"\bqualif", r"\bcitizen", r"\bnationality\b",
        r"\bmust be\b", r"\bage\b", r"\bapplicants?\b", r"\bcandidates?\b",
    ],
    "deadline": [
        r"\bdeadline", r"\bclos(?:e|es|ing)\b", r"\bdue\b", r"\blast date", r"\bno later than",
        r"\btimeline", r"\bschedule", r"\bnotified\b", r"\bnotification", r"\bannounce", _MONTHS,
    ],
    "financial": [
        r"\bincome", r"\bstipend", r"\btuition", r"\bfinancial", r"\bfunding", r"\bfees?\b",
        r"\bpkr\b", r"\busd\b", r"\bsalary", r"\bneed-based", r"\ballowance", r"\bamount",
    ],
    "academic": [
        r"\bacademic", r"\bgpa\b", r"\bcgpa\b", r"\bdegree", r"\buniversit", r"\bsemester",
        r"\bprogram", r"\bdiscipline", r"\bmajor\b", r"\bgrades?\b", r"\benrol",
    ],
}
_COMPILED = {c: [re.compile(p, re.I) for p in pats] for c, pats in _CATEGORY_PATTERNS.items()}


def _score(text: str) -> dict[str, int]:
    return {c: sum(len(rx.findall(text)) for rx in rxs) for c, rxs in _COMPILED.items()}


def classify_category(section_title: str, text: str) -> str:
    """Title keywords win (strongest signal); otherwise fall back to body text."""
    for scores in (_score(section_title), _score(text)):
        best = max(scores.values())
        if best > 0:
            return next(c for c in _CATEGORY_PATTERNS if scores[c] == best)
    return "general"


# --------------------------------------------------------------------------- #
# Section splitting -> units -> chunks
# --------------------------------------------------------------------------- #
def _new_section(number: str, title: str, from_heading: bool) -> dict:
    label = f"Section {number}: {title}" if number else title
    return {"number": number, "title": title, "label": label,
            "from_heading": from_heading, "units": []}


def _split_sections(pages: list[tuple[int, str]]) -> list[dict]:
    cur = _new_section("", "Overview", False)
    sections = [cur]
    buf: list[str] = []
    buf_page = 0

    def flush() -> None:
        nonlocal buf
        if buf:
            cur["units"].append((buf_page, " ".join(buf)))
            buf = []

    for page_no, text in pages:
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                flush()
                continue
            heading = _match_heading(line)
            if heading:
                flush()
                cur = _new_section(heading[0], heading[1], True)
                sections.append(cur)
            elif _BULLET.match(line):
                flush()
                buf, buf_page = [line], page_no
            else:
                if not buf:
                    buf_page = page_no
                buf.append(line)
        flush()  # never let a paragraph span pages (keeps page numbers exact)
    return [s for s in sections if s["units"]]


def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces, cur = [], ""
    for sent in re.split(r"(?<=[.!?])\s+", text):
        while len(sent) > max_chars:  # pathological: no punctuation
            if cur:
                pieces.append(cur)
                cur = ""
            pieces.append(sent[:max_chars])
            sent = sent[max_chars:]
        if cur and len(cur) + 1 + len(sent) > max_chars:
            pieces.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    if cur:
        pieces.append(cur)
    return pieces


def _pack_units(units: list[tuple[int, str]], max_chars: int) -> list[tuple[str, int, int]]:
    """Greedy-pack units into chunks. Returns (text, first_page, last_page)."""
    chunks: list[tuple[str, int, int]] = []
    cur: list[str] = []
    cur_len = 0
    first = last = 0
    for page, text in units:
        for piece in _split_long(text, max_chars):
            if cur and cur_len + len(piece) + 1 > max_chars:
                chunks.append(("\n".join(cur), first, last))
                cur, cur_len = [], 0
            if not cur:
                first = page
            cur.append(piece)
            cur_len += len(piece) + 1
            last = page
    if cur:
        chunks.append(("\n".join(cur), first, last))
    return chunks


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "doc"


def chunk_pages(pages: Iterable[Any], source: str, max_chars: int = MAX_CHARS) -> list[Chunk]:
    """Main entry point: pages -> list[Chunk] with full metadata."""
    norm = normalize_pages(pages)
    sections = _split_sections(norm)
    has_headings = any(s["from_heading"] for s in sections)

    if not has_headings:  # no structure at all -> one pseudo-section per page
        by_page: dict[int, list] = {}
        for sec in sections:
            for page, text in sec["units"]:
                by_page.setdefault(page, []).append((page, text))
        sections = [{"number": "", "title": f"Page {p}", "label": f"Page {p}",
                     "from_heading": False, "units": u} for p, u in sorted(by_page.items())]

    chunks: list[Chunk] = []
    for sec in sections:
        for text, p_first, p_last in _pack_units(sec["units"], max_chars):
            if has_headings:
                label, number, title = sec["label"], sec["number"], sec["title"]
            else:  # no headings anywhere -> cite by page
                label, number, title = f"Page {p_first}", "", f"Page {p_first}"
            idx = len(chunks)
            chunks.append(Chunk(
                id=f"{_slug(source)}-{idx:03d}",
                text=text, source=source, section=label,
                section_number=number, section_title=title,
                page=p_first, page_end=p_last,
                category=classify_category(title if has_headings else "", text),
                chunk_index=idx,
            ))
    return chunks
