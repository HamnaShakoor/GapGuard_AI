from agents.gap_agent import analyze_requirement
from schemas import DocumentRecord, GapAnalysisItem, Requirement, StatusEnum


def make_req():
    return Requirement(
        req_id="R1",
        description="Official transcript showing CGPA of 3.5 or above",
        req_type="MANDATORY",
    )


def make_doc(file_name="transcript.pdf", text="CGPA: 3.8"):
    return DocumentRecord(
        doc_id="d1",
        file_name=file_name,
        doc_type="TRANSCRIPT",
        extracted_text=text,
        metadata={"cgpa": 3.8},
    )


def make_fake(verdict):
    calls = {"count": 0, "prompt": None}

    def fake(prompt, schema):
        calls["count"] += 1
        calls["prompt"] = prompt
        return schema(**verdict)

    return fake, calls


def test_complete_with_real_file():
    fake, _ = make_fake({"status": "COMPLETE", "matched_file": "transcript.pdf",
                         "evidence_text": "CGPA: 3.8", "reason": "CGPA is 3.8"})
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert isinstance(item, GapAnalysisItem)
    assert item.status == StatusEnum.COMPLETE
    assert item.evidence.source_file == "transcript.pdf"
    assert item.evidence.text_snippet == "CGPA: 3.8"


def test_no_documents_is_missing_without_llm_call():
    fake, calls = make_fake({"status": "COMPLETE", "matched_file": "x.pdf", "reason": "x"})
    item = analyze_requirement(make_req(), [], fake)

    assert item.status == StatusEnum.MISSING
    assert item.evidence is None
    assert calls["count"] == 0


def test_complete_with_unknown_file_becomes_warning():
    fake, _ = make_fake({"status": "COMPLETE", "matched_file": "invented.pdf", "reason": "looks fine"})
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == StatusEnum.WARNING
    assert item.evidence is None


def test_missing_has_no_evidence():
    fake, _ = make_fake({"status": "MISSING", "matched_file": "transcript.pdf", "reason": "nothing found"})
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == StatusEnum.MISSING
    assert item.evidence is None


def test_llm_failure_becomes_warning():
    def broken(prompt, schema):
        raise ValueError("LLM returned invalid JSON twice")

    item = analyze_requirement(make_req(), [make_doc()], broken)
    assert item.status == StatusEnum.WARNING


def test_prompt_contains_requirement_and_document():
    fake, calls = make_fake({"status": "WARNING", "matched_file": "transcript.pdf", "reason": "CGPA low"})
    analyze_requirement(make_req(), [make_doc(text="UNIQUE DOC TEXT 999")], fake)

    assert "Official transcript" in calls["prompt"]
    assert "UNIQUE DOC TEXT 999" in calls["prompt"]


def test_warning_passes_through():
    fake, _ = make_fake({"status": "WARNING", "matched_file": "transcript.pdf",
                         "reason": "CGPA is 3.4, minimum is 3.5"})
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == StatusEnum.WARNING
    assert item.evidence.source_file == "transcript.pdf"
