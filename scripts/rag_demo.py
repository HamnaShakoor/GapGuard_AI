"""Quick end-to-end check of the RAG module (your Member-1 deliverable).

    python scripts/rag_demo.py                      # real embeddings (needs HF model download)
    EMBEDDING_BACKEND=hash python scripts/rag_demo.py   # offline lexical embeddings

Expected: "recommendation letter" -> Section 4: Recommendation Letter, page 2.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag import get_all_chunks, ingest_requirements, retrieve_chunks, vectorstore  # noqa: E402

PDF = ROOT / "data" / "requirements" / "sample_scholarship_requirements.pdf"

QUERIES = [
    ("recommendation letter", "documents"),
    ("personal statement word limit", "documents"),
    ("application deadline", "deadline"),
    ("household income limit", "financial"),
    ("minimum CGPA", "eligibility"),
    ("proof of enrollment", None),
]


def main() -> None:
    if not PDF.exists():
        from scripts.make_sample_requirements_pdf import main as make_pdf
        make_pdf()

    n = ingest_requirements(str(PDF))
    print(f"Backend: {vectorstore.embedding_backend()} | stored {n} chunks\n")

    print("== Chunks ==")
    for c in get_all_chunks():
        print(f"  [{c.category:<11}] p{c.page}  {c.section}")

    print("\n== Retrieval ==")
    for q, cat in QUERIES:
        print(f"\nQ: {q!r}  (category={cat})")
        for r in retrieve_chunks(q, cat, k=2):
            print(f"  {r.score:.2f}  {r.section} (p{r.page}) -> {r.text[:80]!r}")


if __name__ == "__main__":
    main()
