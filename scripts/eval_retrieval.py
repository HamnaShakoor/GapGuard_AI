"""Measure RAG retrieval quality -> real numbers for your presentation.

    python scripts/eval_retrieval.py                      # uses the sample requirements PDF
    python scripts/eval_retrieval.py --pdf data/requirements/<official>.pdf

For each test case we check whether the EXPECTED section (and page) is retrieved:
    Hit@1 = expected section is the top result
    Hit@3 = expected section is in the top 3
It also checks chunk category labels against expected ones.

Writes docs/rag_eval_results.md. Report ONLY these measured numbers, and say which
embedding backend produced them. CASES below match the sample PDF; if you evaluate the
official requirements PDF, edit CASES (expected section text + page) to match it.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag import get_all_chunks, ingest_requirements, retrieve_chunks, vectorstore  # noqa: E402

DEFAULT_PDF = ROOT / "data" / "requirements" / "sample_scholarship_requirements.pdf"
OUT_MD = ROOT / "docs" / "rag_eval_results.md"

# (query, category filter, expected section substring, expected page)
CASES = [
    ("recommendation letter from an academic referee", "documents", "Recommendation Letter", 2),
    ("personal statement word limit", "documents", "Personal Statement", 2),
    ("list of mandatory documents", "documents", "Required Documents", 2),
    ("application deadline date", "deadline", "Deadlines", 3),
    ("when will shortlisted candidates be notified", "deadline", "Deadlines", 3),
    ("household income limit", "financial", "Financial Information", 3),
    ("monthly stipend amount", "financial", "Financial Information", 3),
    ("minimum CGPA required", "eligibility", "Eligibility Criteria", 1),
    ("age limit for applicants", "eligibility", "Eligibility Criteria", 1),
    ("forged documents disqualification", None, "Special Conditions", 3),
]

# expected category per section substring (checks the chunker's metadata labels)
EXPECTED_CATEGORY = {
    "Eligibility Criteria": "eligibility",
    "Required Documents": "documents",
    "Recommendation Letter": "documents",
    "Personal Statement": "documents",
    "Financial Information": "financial",
    "Deadlines": "deadline",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=str(DEFAULT_PDF))
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        from scripts.make_sample_requirements_pdf import main as make_pdf
        make_pdf()
    n_chunks = ingest_requirements(str(pdf))
    backend = vectorstore.embedding_backend()

    rows, hit1, hit3, page_ok = [], 0, 0, 0
    for q, cat, exp_sec, exp_page in CASES:
        res = retrieve_chunks(q, cat, k=3)
        secs = [r.section for r in res]
        h1 = bool(secs) and exp_sec in secs[0]
        h3 = any(exp_sec in s for s in secs)
        pg = bool(res) and res[0].page == exp_page
        hit1 += h1
        hit3 += h3
        page_ok += h1 and pg
        top = f"{res[0].section} (p{res[0].page})" if res else "-"
        rows.append((q, cat or "-", exp_sec, top, "PASS" if h1 else ("top-3" if h3 else "FAIL")))

    chunks = get_all_chunks()
    cat_total = cat_ok = 0
    for c in chunks:
        for sec, exp_cat in EXPECTED_CATEGORY.items():
            if sec in c.section:
                cat_total += 1
                cat_ok += c.category == exp_cat

    total = len(CASES)
    summary = [
        f"Backend: {backend} | PDF: {pdf.name} | chunks: {n_chunks}",
        f"Hit@1: {hit1}/{total}",
        f"Hit@3: {hit3}/{total}",
        f"Top-1 with correct section AND page: {page_ok}/{total}",
        f"Chunk category labels correct: {cat_ok}/{cat_total}",
    ]

    print("\n".join(summary), "\n")
    for r in rows:
        print(f"[{r[4]:<5}] {r[0]!r:<55} -> {r[3]}")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    md = ["# RAG retrieval evaluation (measured)\n"]
    md += [f"- {line}" for line in summary]
    md += ["", "| Query | Category filter | Expected section | Top result | Result |",
           "|---|---|---|---|---|"]
    md += [f"| {q} | {c} | {e} | {t} | {s} |" for q, c, e, t, s in rows]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_MD}")


if __name__ == "__main__":
    main()