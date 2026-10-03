from schemas import RequirementResult, Status

# PLACEHOLDER formula. Team ka asli formula aane pe isko replace karna hai.
MANDATORY_WEIGHT = 2
OPTIONAL_WEIGHT = 1
STATUS_POINTS = {
    Status.COMPLETE: 1.0,
    Status.WARNING: 0.5,
    Status.MISSING: 0.0,
}


def compute_score(results: list[RequirementResult]) -> float:
    """Return readiness score from 0 to 100."""
    if not results:
        return 0.0
    earned = 0.0
    total = 0.0
    for r in results:
        weight = MANDATORY_WEIGHT if r.requirement.mandatory else OPTIONAL_WEIGHT
        total += weight
        earned += weight * STATUS_POINTS[r.status]
    return round(earned / total * 100, 1)