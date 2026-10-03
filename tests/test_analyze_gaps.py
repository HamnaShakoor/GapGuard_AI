from agents.gap_agent import analyze_gaps
from schemas import DocumentRecord, ReadinessReport, Requirement


def make_req(rid, name, mandatory=True):
    return Requirement(
        id=rid,
        name=name,
        category="documents",
        mandatory=mandatory,
        description=f"{name} is required",
        generatable=None,
        source_section="Section 4",
        source_page=4,
    )


def make_doc(filename="transcript.pdf"):
    return DocumentRecord(
        filename=filename,
        doc_type="TRANSCRIPT",
        confidence=0.9,
        text="CGPA: 3.8",
        fields={},
    )


def fake_llm(prompt, schema):
    """Decides the verdict from the requirement name found in the prompt."""
    if "Transcript" in prompt:
        return schema(status="COMPLETE", matched_file="transcript.pdf", reason="CGPA 3.8")
    if "CV" in prompt:
        return schema(status="WARNING", matched_file="transcript.pdf", reason="CV looks old")
    return schema(status="MISSING", matched_file=None, reason="not found")


def test_full_report():
    reqs = [
        make_req("R1", "Transcript"),
        make_req("R2", "CV"),
        make_req("R3", "Passport Photo"),
    ]
    report = analyze_gaps(reqs, [make_doc()], fake_llm)

    assert isinstance(report, ReadinessReport)
    assert report.total == 3
    assert report.completed == 1
    assert report.warnings == 1
    assert report.missing == 1
    assert len(report.items) == 3
    assert len(report.documents) == 1
    # (2*1.0 + 2*0.5 + 2*0.0) / 6 = 50.0
    assert report.score == 50.0


def test_no_requirements():
    report = analyze_gaps([], [make_doc()], fake_llm)
    assert report.total == 0
    assert report.score == 0.0
    assert report.items == []


def test_no_documents_everything_missing():
    reqs = [make_req("R1", "Transcript"), make_req("R2", "CV")]
    report = analyze_gaps(reqs, [], fake_llm)
    assert report.missing == 2
    assert report.score == 0.0