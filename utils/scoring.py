from typing import List, Tuple

from schemas import GapItem

# PLACEHOLDER formula. Replace with the team's real formula when it is agreed.
MANDATORY_WEIGHT = 2
OPTIONAL_WEIGHT = 1
STATUS_POINTS = {
    "COMPLETE": 1.0,
    "WARNING": 0.5,
    "MISSING": 0.0,
}


def compute_score(items: List[GapItem]) -> float:
    """Return readiness score from 0 to 100."""
    if not items:
        return 0.0
    earned = 0.0
    total = 0.0
    for item in items:
        weight = MANDATORY_WEIGHT if item.requirement.mandatory else OPTIONAL_WEIGHT
        total += weight
        earned += weight * STATUS_POINTS[item.status]
    return round(earned / total * 100, 1)


def count_statuses(items: List[GapItem]) -> Tuple[int, int, int]:
    """Return (completed, missing, warnings)."""
    completed = sum(1 for i in items if i.status == "COMPLETE")
    missing = sum(1 for i in items if i.status == "MISSING")
    warnings = sum(1 for i in items if i.status == "WARNING")
    return completed, missing, warnings