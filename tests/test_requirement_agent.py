from agents.requirement_agent import extract_requirements
from schemas import Requirement


def make_fake(items):
    """Fake call_json: returns the given items wrapped in the schema it receives."""
    calls = {}

    def fake(prompt, schema):
        calls["prompt"] = prompt
        return schema(requirements=items)

    return fake, calls


def test_basic_extraction():
    fake, _ = make_fake([
        {
            "id": "R1",
            "name": "Official Transcript",
            "category": "documents",
            "mandatory": True,
            "description": "Official transcript with CGPA",
            "generatable": None,
            "source_section": "Section 4",
            "source_page": 4,
        },
        {
            "id": "R2",
            "name": "Personal Statement",
            "category": "documents",
            "mandatory": False,
            "description": "Max 500 words",
            "generatable": "personal_statement",
            "source_section": "Section 5",
            "source_page": 5,
        },
    ])
    reqs = extract_requirements("some text", fake)

    assert len(reqs) == 2
    assert all(isinstance(r, Requirement) for r in reqs)
    assert reqs[0].mandatory is True
    assert reqs[0].generatable is None
    assert reqs[1].generatable == "personal_statement"
    assert reqs[0].source_page == 4


def test_prompt_contains_requirements_text():
    fake, calls = make_fake([])
    extract_requirements("MY UNIQUE TEXT 123", fake)
    assert "MY UNIQUE TEXT 123" in calls["prompt"]


def test_missing_id_gets_auto_id():
    fake, _ = make_fake([
        {
            "name": "CV",
            "category": "documents",
            "mandatory": True,
            "description": "Updated CV",
        }
    ])
    reqs = extract_requirements("text", fake)
    assert reqs[0].id == "R1"
    assert reqs[0].source_page == 0


def test_bad_item_is_skipped():
    fake, _ = make_fake([
        {"id": "R1"},  # missing name, category, mandatory, description
        {
            "id": "R2",
            "name": "CV",
            "category": "documents",
            "mandatory": True,
            "description": "Updated CV",
        },
    ])
    reqs = extract_requirements("text", fake)
    assert len(reqs) == 1
    assert reqs[0].id == "R2"


def test_unknown_generatable_becomes_none():
    fake, _ = make_fake([
        {
            "id": "R1",
            "name": "CV",
            "category": "documents",
            "mandatory": True,
            "description": "Updated CV",
            "generatable": "something_random",
        }
    ])
    reqs = extract_requirements("text", fake)
    assert reqs[0].generatable is None


def test_empty_response():
    fake, _ = make_fake([])
    assert extract_requirements("text", fake) == []