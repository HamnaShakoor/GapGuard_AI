import os
from typing import List

from pydantic import BaseModel, ValidationError

from schemas import Requirement

PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "requirement_prompt.txt",
)

TRUE_WORDS = {"true", "yes", "personal_statement", "recommendation_email"}


class RawRequirements(BaseModel):
    """Loose wrapper so one bad item does not fail the whole LLM answer."""

    requirements: List[dict] = []


def load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _default_llm_call(prompt, schema):
    # Imported here so tests do not need the groq library or an API key
    from llm.client import call_json

    return call_json(prompt, schema)


def extract_requirements(requirements_text: str, llm_call=None) -> List[Requirement]:
    """Turn raw scholarship requirements text into a list of Requirement objects."""
    if llm_call is None:
        llm_call = _default_llm_call

    prompt = load_prompt().format(requirements_text=requirements_text)
    raw = llm_call(prompt, RawRequirements)

    results = []
    for i, item in enumerate(raw.requirements, start=1):
        item = dict(item)
        item.setdefault("req_id", item.get("id") or f"R{i}")

        req_type = str(item.get("req_type", "")).strip().upper()
        item["req_type"] = req_type if req_type in ("MANDATORY", "OPTIONAL") else "MANDATORY"

        gen = item.get("generatable")
        item["generatable"] = gen is True or str(gen).strip().lower() in TRUE_WORDS

        try:
            results.append(
                Requirement(
                    req_id=str(item["req_id"]),
                    description=item.get("description"),
                    req_type=item["req_type"],
                    generatable=item["generatable"],
                )
            )
        except (ValidationError, TypeError):
            continue  # skip a malformed item instead of crashing everything
    return results
