import time
from typing import List, Optional
from schemas import (
    ReadinessReport, 
    GapAnalysisItem, 
    Requirement, 
    RequirementType, 
    StatusEnum, 
    Evidence, 
    GenerationOutput, 
    StepCallback
)


class PipelineOrchestrator:
    def __init__(self, callback: Optional[StepCallback] = None):
        self.callback = callback

    def _emit_step(self, step_name: str, status_msg: str) -> None:
        if self.callback:
            self.callback(step_name, status_msg)

    def run_pipeline(self, document_paths: List[str]) -> ReadinessReport:
        self._emit_step("Ingestion", "Reading and parsing uploaded documents...")
        time.sleep(0.5)

        self._emit_step("Classification", "Classifying document types and extracting metadata...")
        time.sleep(0.5)

        self._emit_step("Analysis", "Comparing extracted evidence against scholarship requirements...")
        time.sleep(0.5)

        # Updated mock report matching exact list length (2 gap items)
        mock_report = ReadinessReport(
            overall_score=75.0,
            total_requirements=2,  # Fixed: set to 2 to match len(gap_items)
            completed_count=1,
            missing_count=1,
            warning_count=0,
            gap_items=[
                GapAnalysisItem(
                    requirement=Requirement(
                        req_id="REQ-001",
                        description="Minimum GPA of 3.5 on Transcript",
                        req_type=RequirementType.MANDATORY,
                        generatable=False
                    ),
                    status=StatusEnum.COMPLETE,
                    evidence=Evidence(
                        source_file="transcript.pdf",
                        section="Academic Standing",
                        page=1,
                        text_snippet="Cumulative GPA: 3.82"
                    ),
                    notes="Requirement satisfied."
                ),
                GapAnalysisItem(
                    requirement=Requirement(
                        req_id="REQ-002",
                        description="Recommendation Letter from Department Chair",
                        req_type=RequirementType.MANDATORY,
                        generatable=True
                    ),
                    status=StatusEnum.MISSING,
                    evidence=None,
                    notes="Document missing. Email request can be auto-generated."
                )
            ]
        )

        self._emit_step("Complete", "Readiness Report successfully generated.")
        return mock_report

    def trigger_generation(self, target_type: str, gap_item: GapAnalysisItem) -> GenerationOutput:
        self._emit_step("Generation", f"Generating missing document artifact: {target_type}...")
        time.sleep(0.5)
        
        return GenerationOutput(
            generated_text="Subject: Recommendation Letter Request\n\nDear Professor,\n\nI am applying for the National AI Excellence Scholarship 2026...",
            doc_type=target_type,
            placeholders_used=["[Professor Name]", "[Course Code]"]
        )