from schemas import *
from agents.generation_agent import generate

req = Requirement(
    id="R5",
    name="Recommendation Letter",
    category="documents",
    mandatory=True,
    description="One recommendation letter from an academic referee, maximum 200 words",
    generatable="recommendation_email",
    source_section="Section 3",
    source_page=3,
)
doc = DocumentRecord(
    filename="cv.pdf",
    doc_type=DocType.CV,
    confidence=0.9,
    text="...",
    fields={
        "name": "Ayesha Khan",
        "education": "BS Computer Science, CGPA 3.6",
        "skills": ["Python", "machine learning"],
        "projects": ["Student attendance app"],
    },
)
item = GapItem(
    requirement=req,
    status="MISSING",
    reason="Required",
    evidence=Evidence(
        text="Applicants must submit one academic recommendation.",
        section="Section 3",
        page=3,
    ),
)
report = ReadinessReport(
    score=0,
    completed=0,
    missing=1,
    warnings=0,
    total=1,
    items=[item],
    documents=[doc],
)

out = generate("recommendation_email", report, "R5")
print(out.title)
print(out.body)
print("Words:", len(out.body.split()))
print("Placeholders:", out.placeholders)