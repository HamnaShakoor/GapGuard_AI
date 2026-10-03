from schemas import Requirement, RequirementResult, Status
from utils.scoring import compute_score


def make(status, mandatory=True):
    req = Requirement(id="r", title="t", description="d", mandatory=mandatory)
    return RequirementResult(requirement=req, status=status)


def test_all_complete():
    assert compute_score([make(Status.COMPLETE)] * 3) == 100.0


def test_all_missing():
    assert compute_score([make(Status.MISSING)] * 3) == 0.0


def test_warning_is_half():
    assert compute_score([make(Status.WARNING)]) == 50.0


def test_mandatory_weighs_more():
    results = [make(Status.COMPLETE, True), make(Status.MISSING, False)]
    assert compute_score(results) == 66.7


def test_empty():
    assert compute_score([]) == 0.0