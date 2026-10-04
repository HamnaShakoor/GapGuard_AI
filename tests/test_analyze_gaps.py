from agents.gap_agent import analyze_gaps
from schemas import DocumentRecord, ReadinessReport, Requirement


def make_req(rid, text, mandatory=True):
    return Requirement(
        req_id=rid,
        description=text,
        req_type="MANDATORY" if mandatory else "OPTIONAL",
    )


def make_doc(file_name="transcript.pdf"):
    return DocumentRecord(
        doc_id="d1",
        file_name=file_name,
        doc_type="TRANSCRIPT",
        extracted_text="CGPA: 3.8",
        metadata={},
    )


def fake_llm(prompt, schema):
    if "Transcript" in prompt:
        return schema(status="COMPLETE", matched_file="transcript.pdf", reason="CGPA 3.8")
    if "CV" in prompt:
        return schema(status="WARNING", matched_file="transcript.pdf", reason="CV looks old")
    return schema(status="MISSING", matched_file=None, reason="not found")


def test_full_report():
    reqs = [make_req("R1", "Transcript"), make_req("R2", "CV"), make_req("R3", "Passport Photo")]
    report = analyze_gaps(reqs, [make_doc()], fake_llm)

    assert isinstance(report, ReadinessReport)
    assert report.total_requirements == 3
    assert report.completed_count == 1
    assert report.warning_count == 1
    assert report.missing_count == 1
    assert len(report.gap_items) == 3
    assert report.overall_score == 50.0


def test_no_requirements():
    report = analyze_gaps([], [make_doc()], fake_llm)
    assert report.total_requirements == 0
    assert report.overall_score == 0.0
    assert report.gap_items == []


def test_no_documents_everything_missing():
    reqs = [make_req("R1", "Transcript"), make_req("R2", "CV")]
    report = analyze_gaps(reqs, [], fake_llm)
    assert report.missing_count == 2
    assert report.overall_score == 0.0
