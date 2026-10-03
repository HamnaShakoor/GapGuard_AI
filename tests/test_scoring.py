from schemas import Evidence, GapItem, Requirement
from utils.scoring import compute_score, count_statuses


def make(status, mandatory=True):
    req = Requirement(
        id="r",
        name="n",
        category="documents",
        mandatory=mandatory,
        description="d",
        source_section="Section 1",
        source_page=1,
    )
    return GapItem(
        requirement=req,
        status=status,
        matched_file=None,
        reason="",
        evidence=Evidence(text="d", section="Section 1", page=1),
    )


def test_all_complete():
    assert compute_score([make("COMPLETE")] * 3) == 100.0


def test_all_missing():
    assert compute_score([make("MISSING")] * 3) == 0.0


def test_warning_is_half():
    assert compute_score([make("WARNING")]) == 50.0


def test_mandatory_weighs_more():
    items = [make("COMPLETE", True), make("MISSING", False)]
    assert compute_score(items) == 66.7


def test_empty():
    assert compute_score([]) == 0.0


def test_count_statuses():
    items = [make("COMPLETE"), make("COMPLETE"), make("MISSING"), make("WARNING")]
    assert count_statuses(items) == (2, 1, 1)