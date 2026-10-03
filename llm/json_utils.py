import json
import re

from pydantic import BaseModel, ValidationError


def extract_json(raw: str) -> dict:
    """Pull a JSON object out of messy model output."""
    text = raw.strip()

    # remove ```json ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # fall back: grab the first {...} block
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])

    raise json.JSONDecodeError("No JSON object found", text, 0)


def parse_and_validate(raw: str, schema: type[BaseModel]) -> BaseModel:
    """Extract JSON and validate it against a Pydantic schema."""
    return schema.model_validate(extract_json(raw))