from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel, Field


class RequirementType(str, Enum):
    MANDATORY = "MANDATORY"
    OPTIONAL = "OPTIONAL"


class StatusEnum(str, Enum):
    COMPLETE = "COMPLETE"
    MISSING = "MISSING"
    WARNING = "WARNING"


class DocType(str, Enum):
    TRANSCRIPT = "TRANSCRIPT"
    CV = "CV"
    RECOMMENDATION_LETTER = "RECOMMENDATION_LETTER"
    PERSONAL_STATEMENT = "PERSONAL_STATEMENT"
    REQUIREMENTS_SPEC = "REQUIREMENTS_SPEC"
    UNKNOWN = "UNKNOWN"


class DocumentRecord(BaseModel):
    doc_id: str
    file_name: str
    doc_type: DocType
    extracted_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    source_file: str
    section: Optional[str] = None
    page: Optional[int] = None
    text_snippet: str


class Requirement(BaseModel):
    req_id: str
    description: str
    req_type: RequirementType
    generatable: bool = False


class GapAnalysisItem(BaseModel):
    requirement: Requirement
    status: StatusEnum
    evidence: Optional[Evidence] = None
    notes: Optional[str] = None


class ReadinessReport(BaseModel):
    overall_score: float
    total_requirements: int
    completed_count: int
    missing_count: int
    warning_count: int
    gap_items: List[GapAnalysisItem]


class GenerationOutput(BaseModel):
    generated_text: str
    doc_type: str
    placeholders_used: List[str] = Field(default_factory=list)


# Step Callback Type Signature for UI updates
StepCallback = Callable[[str, str], None]