import json
import os
from typing import List, Literal, Optional

from pydantic import BaseModel

from schemas import DocumentRecord, Evidence, GapItem, ReadinessReport, Requirement
from utils.scoring import compute_score, count_statuses

PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "gap_prompt.txt",
)

MAX_TEXT_PER_DOC = 3000  # characters of each document sent to the LLM


class GapVerdict(BaseModel):
    """What we ask the LLM to return for ONE requirement."""

    status: Literal["COMPLETE", "MISSING", "WARNING"]
    matched_file: Optional[str] = None
    reason: str = ""


def load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _default_llm_call(prompt, schema):
    # Imported here so tests do not need the groq library or an API key
    from llm.client import call_json

    return call_json(prompt, schema)


def summarize_documents(documents: List[DocumentRecord]) -> str:
    """Turn the student's documents into one text block for the prompt."""
    parts = []
    for d in documents:
        doc_type = getattr(d.doc_type, "value", d.doc_type)
        fields = json.dumps(d.fields, ensure_ascii=False)
        parts.append(
            f"--- File: {d.filename} (type: {doc_type}) ---\n"
            f"Key fields: {fields}\n"
            f"Text:\n{d.text[:MAX_TEXT_PER_DOC]}"
        )
    return "\n\n".join(parts)


def _evidence_from(requirement: Requirement) -> Evidence:
    """Where the requirement comes from in the scholarship document."""
    return Evidence(
        text=requirement.description,
        section=requirement.source_section,
        page=requirement.source_page,
    )


def analyze_requirement(
    requirement: Requirement,
    documents: List[DocumentRecord],
    llm_call=None,
) -> GapItem:
    """Check ONE requirement against the student's documents.

    llm_call(prompt, schema) is Member 4's call_json by default.
    Tests pass a fake function instead.
    """
    if llm_call is None:
        llm_call = _default_llm_call

    evidence = _evidence_from(requirement)

    # Rule 1: no documents at all -> MISSING, no need to call the LLM
    if not documents:
        return GapItem(
            requirement=requirement,
            status="MISSING",
            matched_file=None,
            reason="No documents were uploaded.",
            evidence=evidence,
        )

    prompt = load_prompt().format(
        requirement_name=requirement.name,
        requirement_category=requirement.category,
        requirement_description=requirement.description,
        documents_summary=summarize_documents(documents),
    )

    try:
        verdict = llm_call(prompt, GapVerdict)
    except Exception:
        # If the LLM fails, do not crash the whole pipeline
        return GapItem(
            requirement=requirement,
            status="WARNING",
            matched_file=None,
            reason="Could not analyze this requirement automatically. Please check manually.",
            evidence=evidence,
        )

    status = verdict.status
    matched_file = verdict.matched_file
    reason = verdict.reason.strip()

    # Rule 2: the file the LLM names must really be one of the uploaded files
    known_files = {d.filename for d in documents}
    if matched_file not in known_files:
        matched_file = None

    # Rule 3: COMPLETE without a real matched file is not trustworthy
    if status == "COMPLETE" and matched_file is None:
        status = "WARNING"
        reason = "Marked complete but no matching uploaded file was found. Please check manually."

    # MISSING means no matched file by definition
    if status == "MISSING":
        matched_file = None

    return GapItem(
        requirement=requirement,
        status=status,
        matched_file=matched_file,
        reason=reason,
        evidence=evidence,
    )
    
    
def analyze_gaps(
    requirements: List[Requirement],
    documents: List[DocumentRecord],
    llm_call=None,
) -> ReadinessReport:
    """Main deliverable: compare every requirement with the student's documents."""
    items = [analyze_requirement(req, documents, llm_call) for req in requirements]
    completed, missing, warnings = count_statuses(items)
    return ReadinessReport(
        score=compute_score(items),
        completed=completed,
        missing=missing,
        warnings=warnings,
        total=len(items),
        items=items,
        documents=documents,
    )