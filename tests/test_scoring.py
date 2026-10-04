from schemas import GapAnalysisItem, Requirement
from utils.scoring import compute_score, count_statuses


def make(status, mandatory=True):
    req = Requirement(
        req_id="r",
        description="d",
        req_type="MANDATORY" if mandatory else "OPTIONAL",
    )
    return GapAnalysisItem(requirement=req, status=status)


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
