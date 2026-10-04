from agents.requirement_agent import extract_requirements
from schemas import Requirement, RequirementType


def make_fake(items):
    calls = {}

    def fake(prompt, schema):
        calls["prompt"] = prompt
        return schema(requirements=items)

    return fake, calls


def test_basic_extraction():
    fake, _ = make_fake([
        {"req_id": "R1", "description": "Official transcript", "req_type": "MANDATORY", "generatable": False},
        {"req_id": "R2", "description": "Personal statement", "req_type": "OPTIONAL", "generatable": True},
    ])
    reqs = extract_requirements("some text", fake)

    assert len(reqs) == 2
    assert all(isinstance(r, Requirement) for r in reqs)
    assert reqs[0].req_type == RequirementType.MANDATORY
    assert reqs[1].req_type == RequirementType.OPTIONAL
    assert reqs[0].generatable is False
    assert reqs[1].generatable is True


def test_prompt_contains_requirements_text():
    fake, calls = make_fake([])
    extract_requirements("MY UNIQUE TEXT 123", fake)
    assert "MY UNIQUE TEXT 123" in calls["prompt"]


def test_missing_id_gets_auto_id():
    fake, _ = make_fake([{"description": "Updated CV", "req_type": "MANDATORY"}])
    reqs = extract_requirements("text", fake)
    assert reqs[0].req_id == "R1"


def test_bad_item_is_skipped():
    fake, _ = make_fake([
        {"req_id": "R1"},  # no description
        {"req_id": "R2", "description": "CV", "req_type": "MANDATORY"},
    ])
    reqs = extract_requirements("text", fake)
    assert len(reqs) == 1
    assert reqs[0].req_id == "R2"


def test_unknown_req_type_defaults_to_mandatory():
    fake, _ = make_fake([{"req_id": "R1", "description": "CV", "req_type": "weird"}])
    reqs = extract_requirements("text", fake)
    assert reqs[0].req_type == RequirementType.MANDATORY


def test_empty_response():
    fake, _ = make_fake([])
    assert extract_requirements("text", fake) == []
