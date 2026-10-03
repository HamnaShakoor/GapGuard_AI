import json
import re

from pydantic import BaseModel

import config
from llm.client import call_json
from schemas import GeneratedContent, ReadinessReport

PROMPT_FILES = {
    "personal_statement": "personal_statement_prompt.txt",
    "recommendation_email": "recommendation_email_prompt.txt",
    "checklist": "checklist_prompt.txt",
}
DEFAULT_WORD_LIMIT = 500


class _Draft(BaseModel):
    title: str
    body: str
    placeholders: list[str] = []


def _facts(report: ReadinessReport) -> dict:
    facts = {}
    for d in report.documents:
        key = getattr(d.doc_type, "value", str(d.doc_type))
        if d.fields:
            facts[key] = d.fields
    return facts


def _word_limit(req) -> int:
    m = re.search(r"(\d+)\s*words?", f"{req.name} {req.description}", re.I)
    return int(m.group(1)) if m else DEFAULT_WORD_LIMIT

def _checklist_text(report: ReadinessReport) -> str:
    lines = []
    for i in report.items:
        r = i.requirement
        kind = "mandatory" if r.mandatory else "optional"
        lines.append(f"- [{i.status}] {r.name} ({kind}): {i.reason}")
    return "\n".join(lines)


def generate(kind: str, report: ReadinessReport, requirement_id: str) -> GeneratedContent:
    if kind == "checklist":
        template = (config.PROMPTS_DIR / PROMPT_FILES[kind]).read_text(encoding="utf-8")
        prompt = template.replace("<<SCORE>>", str(report.score)).replace(
            "<<ITEMS>>", _checklist_text(report)
        )
        draft = call_json(prompt, _Draft)
        return GeneratedContent(
            kind=kind, title=draft.title, body=draft.body, placeholders=[]
        )
    req = next(
        (i.requirement for i in report.items if i.requirement.id == requirement_id),
        None,
    )
    if req is None:
        raise ValueError(f"Requirement {requirement_id} not found")

    limit = _word_limit(req)
    template = (config.PROMPTS_DIR / PROMPT_FILES[kind]).read_text(encoding="utf-8")
    prompt = (
        template.replace("<<WORD_LIMIT>>", str(limit))
        .replace("<<REQUIREMENT>>", f"{req.name}: {req.description}")
        .replace("<<FACTS>>", json.dumps(_facts(report), indent=2))
    )

    draft = call_json(prompt, _Draft)
    for _ in range(2):  # shorten up to twice if over the limit
        words = len(draft.body.split())
        if words <= limit:
            break
        draft = call_json(
            prompt + f"\n\nYour last draft had {words} words. Rewrite it under {limit} words.",
            _Draft,
        )

    found = re.findall(r"\[[A-Z0-9 _\-]+\]", draft.body)
    cleaned = {p if p.startswith("[") else f"[{p}]" for p in draft.placeholders}
    placeholders = sorted(cleaned | set(found))
    return GeneratedContent(
        kind=kind, title=draft.title, body=draft.body, placeholders=placeholders
    )