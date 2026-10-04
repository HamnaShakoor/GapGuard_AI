import json
import os
from typing import List, Literal, Optional

from pydantic import BaseModel

from schemas import (
    DocumentRecord,
    Evidence,
    GapAnalysisItem,
    ReadinessReport,
    Requirement,
    StatusEnum,
)
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
    evidence_text: Optional[str] = None
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
        meta = json.dumps(d.metadata, ensure_ascii=False, default=str)
        parts.append(
            f"--- File: {d.file_name} (type: {doc_type}) ---\n"
            f"Key fields: {meta}\n"
            f"Text:\n{d.extracted_text[:MAX_TEXT_PER_DOC]}"
        )
    return "\n\n".join(parts)


def analyze_requirement(
    requirement: Requirement,
    documents: List[DocumentRecord],
    llm_call=None,
) -> GapAnalysisItem:
    """Check ONE requirement against the student's documents."""
    if llm_call is None:
        llm_call = _default_llm_call

    # Rule 1: no documents at all -> MISSING, no need to call the LLM
    if not documents:
        return GapAnalysisItem(
            requirement=requirement,
            status=StatusEnum.MISSING,
            evidence=None,
            notes="No documents were uploaded.",
        )

    prompt = load_prompt().format(
        requirement_type=requirement.req_type.value,
        requirement_description=requirement.description,
        documents_summary=summarize_documents(documents),
    )

    try:
        verdict = llm_call(prompt, GapVerdict)
    except Exception:
        # If the LLM fails, do not crash the whole pipeline
        return GapAnalysisItem(
            requirement=requirement,
            status=StatusEnum.WARNING,
            evidence=None,
            notes="Could not analyze this requirement automatically. Please check manually.",
        )

    status = StatusEnum(verdict.status)
    notes = verdict.reason.strip()
    matched_file = verdict.matched_file

    # Rule 2: the file the LLM names must really be one of the uploaded files
    known_files = {d.file_name for d in documents}
    if matched_file not in known_files:
        matched_file = None

    # Rule 3: COMPLETE without a real matched file is not trustworthy
    if status == StatusEnum.COMPLETE and matched_file is None:
        status = StatusEnum.WARNING
        notes = "Marked complete but no matching uploaded file was found. Please check manually."

    # MISSING means no evidence by definition
    if status == StatusEnum.MISSING:
        matched_file = None

    evidence = None
    if matched_file is not None:
        evidence = Evidence(
            source_file=matched_file,
            section=None,
            page=None,
            text_snippet=(verdict.evidence_text or notes or "").strip(),
        )

    return GapAnalysisItem(
        requirement=requirement,
        status=status,
        evidence=evidence,
        notes=notes,
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
        overall_score=compute_score(items),
        total_requirements=len(items),
        completed_count=completed,
        missing_count=missing,
        warning_count=warnings,
        gap_items=items,
    )
