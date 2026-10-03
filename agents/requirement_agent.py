import os
from typing import List

from pydantic import BaseModel, ValidationError

from schemas import Requirement

PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "requirement_prompt.txt",
)

ALLOWED_GENERATABLE = {"personal_statement", "recommendation_email"}


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
    """Turn raw scholarship requirements text into a list of Requirement objects.

    llm_call(prompt, schema) is Member 4's call_json by default.
    Tests pass a fake function instead.
    """
    if llm_call is None:
        llm_call = _default_llm_call

    prompt = load_prompt().format(requirements_text=requirements_text)
    raw = llm_call(prompt, RawRequirements)

    results = []
    for i, item in enumerate(raw.requirements, start=1):
        item = dict(item)
        item.setdefault("id", f"R{i}")
        if item.get("source_page") is None:
            item["source_page"] = 0
        if item.get("source_section") is None:
            item["source_section"] = ""
        if item.get("generatable") not in ALLOWED_GENERATABLE:
            item["generatable"] = None
        try:
            results.append(Requirement(**item))
        except (ValidationError, TypeError):
            # Skip a malformed item instead of crashing the whole pipeline
            continue
    return results