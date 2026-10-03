from agents.requirement_agent import extract_requirements
from schemas import Requirement


class FakeLLM:
    """Pretends to be the LLM and returns a ready-made answer."""

    def __init__(self, response):
        self.response = response
        self.last_prompt = None

    def generate_json(self, prompt):
        self.last_prompt = prompt
        return self.response


def test_basic_extraction():
    fake = FakeLLM({
        "requirements": [
            {
                "id": "R1",
                "title": "Transcript",
                "description": "Official transcript with CGPA",
                "mandatory": True,
                "generatable": False,
                "source_section": "Section 4",
                "source_page": 4,
            },
            {
                "id": "R2",
                "title": "Personal statement",
                "description": "Max 500 words",
                "mandatory": False,
                "generatable": True,
                "source_section": "Section 5",
                "source_page": 5,
            },
        ]
    })
    reqs = extract_requirements("some requirements text", fake)

    assert len(reqs) == 2
    assert all(isinstance(r, Requirement) for r in reqs)
    assert reqs[0].mandatory is True
    assert reqs[0].generatable is False
    assert reqs[1].generatable is True
    assert reqs[0].source_page == 4


def test_prompt_contains_requirements_text():
    fake = FakeLLM({"requirements": []})
    extract_requirements("MY UNIQUE TEXT 123", fake)
    assert "MY UNIQUE TEXT 123" in fake.last_prompt


def test_missing_id_gets_auto_id():
    fake = FakeLLM({
        "requirements": [{"title": "CV", "description": "Updated CV"}]
    })
    reqs = extract_requirements("text", fake)
    assert reqs[0].id == "R1"


def test_bad_item_is_skipped():
    fake = FakeLLM({
        "requirements": [
            {"id": "R1"},  # missing title and description
            {"id": "R2", "title": "CV", "description": "Updated CV"},
        ]
    })
    reqs = extract_requirements("text", fake)
    assert len(reqs) == 1
    assert reqs[0].id == "R2"


def test_empty_response():
    fake = FakeLLM({})
    assert extract_requirements("text", fake) == []