from schemas import *
from agents.generation_agent import generate

req = Requirement(
    id="R7", name="Personal Statement",
    category="documents", mandatory=True,
    description="Personal statement of maximum 300 words",
    generatable="personal_statement",
    source_section="Section 4", source_page=4,
)
doc = DocumentRecord(
    filename="cv.pdf", doc_type=DocType.CV, confidence=0.9, text="...",
    fields={"name": "Ayesha Khan", "education": "BS Computer Science, CGPA 3.6",
            "skills": ["Python", "machine learning"],
            "projects": ["Student attendance app"]},
)
item = GapItem(
    requirement=req, status="MISSING", reason="Required",
    evidence=Evidence(text="Applicants must submit a personal statement.",
                      section="Section 4", page=4),
)
report = ReadinessReport(score=0, completed=0, missing=1, warnings=0,
                         total=1, items=[item], documents=[doc])

out = generate("personal_statement", report, "R7")
print(out.title)
print(out.body)
print("Words:", len(out.body.split()))
print("Placeholders:", out.placeholders)