from agents.gap_agent import analyze_requirement
from schemas import DocumentRecord, GapItem, Requirement


def make_req():
    return Requirement(
        id="R1",
        name="Official Transcript",
        category="documents",
        mandatory=True,
        description="Official transcript showing CGPA of 3.5 or above",
        generatable=None,
        source_section="Section 4",
        source_page=4,
    )


def make_doc(filename="transcript.pdf", text="CGPA: 3.8"):
    return DocumentRecord(
        filename=filename,
        doc_type="TRANSCRIPT",
        confidence=0.9,
        text=text,
        fields={"cgpa": 3.8},
    )


def make_fake(verdict):
    """Fake call_json: builds the schema it receives from a plain dict."""
    calls = {"count": 0, "prompt": None}

    def fake(prompt, schema):
        calls["count"] += 1
        calls["prompt"] = prompt
        return schema(**verdict)

    return fake, calls


def test_complete_with_real_file():
    fake, _ = make_fake(
        {"status": "COMPLETE", "matched_file": "transcript.pdf", "reason": "CGPA is 3.8"}
    )
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert isinstance(item, GapItem)
    assert item.status == "COMPLETE"
    assert item.matched_file == "transcript.pdf"
    # evidence comes from the requirement, not from the LLM
    assert item.evidence.section == "Section 4"
    assert item.evidence.page == 4


def test_no_documents_is_missing_without_llm_call():
    fake, calls = make_fake({"status": "COMPLETE", "matched_file": "x.pdf", "reason": "x"})
    item = analyze_requirement(make_req(), [], fake)

    assert item.status == "MISSING"
    assert calls["count"] == 0


def test_complete_with_unknown_file_becomes_warning():
    fake, _ = make_fake(
        {"status": "COMPLETE", "matched_file": "invented.pdf", "reason": "looks fine"}
    )
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == "WARNING"
    assert item.matched_file is None


def test_missing_has_no_matched_file():
    fake, _ = make_fake(
        {"status": "MISSING", "matched_file": "transcript.pdf", "reason": "nothing found"}
    )
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == "MISSING"
    assert item.matched_file is None


def test_llm_failure_becomes_warning():
    def broken(prompt, schema):
        raise ValueError("LLM returned invalid JSON twice")

    item = analyze_requirement(make_req(), [make_doc()], broken)

    assert item.status == "WARNING"
    assert item.evidence.page == 4


def test_prompt_contains_requirement_and_document():
    fake, calls = make_fake(
        {"status": "WARNING", "matched_file": "transcript.pdf", "reason": "CGPA low"}
    )
    analyze_requirement(make_req(), [make_doc(text="UNIQUE DOC TEXT 999")], fake)

    assert "Official Transcript" in calls["prompt"]
    assert "UNIQUE DOC TEXT 999" in calls["prompt"]


def test_warning_passes_through():
    fake, _ = make_fake(
        {"status": "WARNING", "matched_file": "transcript.pdf", "reason": "CGPA is 3.4, minimum is 3.5"}
    )
    item = analyze_requirement(make_req(), [make_doc()], fake)

    assert item.status == "WARNING"
    assert item.matched_file == "transcript.pdf"