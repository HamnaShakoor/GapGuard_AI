import os

from pydantic import ValidationError

from schemas import Requirement

PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "requirement_prompt.txt",
)


def load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def extract_requirements(requirements_text: str, llm_client) -> list[Requirement]:
    """Turn raw scholarship requirements text into a list of Requirement objects."""
    prompt = load_prompt().format(requirements_text=requirements_text)

    # Same call style Member 2 uses in document_agent.py
    response = llm_client.generate_json(prompt)

    items = response.get("requirements", [])
    requirements = []
    for i, item in enumerate(items, start=1):
        item.setdefault("id", f"R{i}")
        try:
            requirements.append(Requirement(**item))
        except ValidationError:
            # Skip a malformed item instead of crashing the whole pipeline
            continue
    return requirements