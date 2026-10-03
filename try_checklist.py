from schemas import *
from agents.generation_agent import generate


def make(id, name, status, mandatory, reason):
    req = Requirement(
        id=id, name=name, category="documents", mandatory=mandatory,
        description=name, generatable=None,
        source_section="Section 3", source_page=3,
    )
    return GapItem(
        requirement=req, status=status, reason=reason,
        evidence=Evidence(text="Required document.", section="Section 3", page=3),
    )


items = [
    make("R1", "CNIC copy", "COMPLETE", True, "Found cnic.pdf"),
    make("R2", "Transcript", "WARNING", True, "Transcript is older than 6 months"),
    make("R3", "Recommendation letter", "MISSING", True, "No letter uploaded"),
    make("R4", "Personal statement", "MISSING", True, "No statement uploaded"),
]
report = ReadinessReport(
    score=50.0, completed=1, missing=2, warnings=1, total=4,
    items=items, documents=[],
)

out = generate("checklist", report, "")
print(out.title)
print(out.body)