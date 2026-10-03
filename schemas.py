# schemas.py
from enum import Enum
from typing import Literal, Optional, List
from pydantic import BaseModel

class DocType(str, Enum):
    CNIC = "CNIC"
    TRANSCRIPT = "TRANSCRIPT"
    CV = "CV"
    PHOTO = "PHOTO"
    RECOMMENDATION = "RECOMMENDATION"
    STATEMENT = "STATEMENT"
    ENROLLMENT = "ENROLLMENT"
    INCOME = "INCOME"
    UNKNOWN = "UNKNOWN"

class DocumentRecord(BaseModel):
    filename: str
    doc_type: DocType
    confidence: float
    text: str
    fields: dict

class Requirement(BaseModel):
    id: str
    name: str
    category: str  # documents | eligibility | deadline | financial | academic
    mandatory: bool
    description: str
    generatable: Optional[str] = None  # "personal_statement" | "recommendation_email" | None
    source_section: str
    source_page: int

class Evidence(BaseModel):
    text: str
    section: str
    page: int

class GapItem(BaseModel):
    requirement: Requirement
    status: Literal["COMPLETE", "MISSING", "WARNING"]
    matched_file: Optional[str] = None
    reason: str
    evidence: Evidence

class ReadinessReport(BaseModel):
    score: float
    completed: int
    missing: int
    warnings: int
    total: int
    items: List[GapItem]
    documents: List[DocumentRecord]

class GeneratedContent(BaseModel):
    kind: str
    title: str
    body: str
    placeholders: List[str]