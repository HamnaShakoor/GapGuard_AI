from typing import List, Tuple

from schemas import GapAnalysisItem, RequirementType, StatusEnum

# PLACEHOLDER formula. Replace with the team's real formula when it is agreed.
MANDATORY_WEIGHT = 2
OPTIONAL_WEIGHT = 1
STATUS_POINTS = {
    StatusEnum.COMPLETE: 1.0,
    StatusEnum.WARNING: 0.5,
    StatusEnum.MISSING: 0.0,
}


def compute_score(items: List[GapAnalysisItem]) -> float:
    """Return readiness score from 0 to 100."""
    if not items:
        return 0.0
    earned = 0.0
    total = 0.0
    for item in items:
        mandatory = item.requirement.req_type == RequirementType.MANDATORY
        weight = MANDATORY_WEIGHT if mandatory else OPTIONAL_WEIGHT
        total += weight
        earned += weight * STATUS_POINTS[item.status]
    return round(earned / total * 100, 1)


def count_statuses(items: List[GapAnalysisItem]) -> Tuple[int, int, int]:
    """Return (completed, missing, warnings)."""
    completed = sum(1 for i in items if i.status == StatusEnum.COMPLETE)
    missing = sum(1 for i in items if i.status == StatusEnum.MISSING)
    warnings = sum(1 for i in items if i.status == StatusEnum.WARNING)
    return completed, missing, warnings
