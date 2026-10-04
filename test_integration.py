import os
import unittest
from schemas import ReadinessReport, StatusEnum
from agents.orchestrator import PipelineOrchestrator


class TestPipelineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = PipelineOrchestrator()
        cls.scenario_1_files = [
            "sample_documents/scenario_1_complete/transcript.txt",
            "sample_documents/scenario_1_complete/cv.txt",
            "sample_documents/scenario_1_complete/recommendation_letter.txt",
            "sample_documents/scenario_1_complete/personal_statement.txt"
        ]
        cls.scenario_2_files = [
            "sample_documents/scenario_2_missing_docs/transcript.txt",
            "sample_documents/scenario_2_missing_docs/cv.txt"
        ]

    def test_pipeline_scenario_1_execution(self):
        """Verify orchestrator runs and produces a valid ReadinessReport."""
        report = self.orchestrator.run_pipeline(self.scenario_1_files)
        self.assertIsInstance(report, ReadinessReport)
        self.assertGreaterEqual(report.overall_score, 0.0)
        self.assertLessEqual(report.overall_score, 100.0)

    def test_trigger_generation(self):
        """Verify downstream artifact generation callbacks work correctly."""
        report = self.orchestrator.run_pipeline(self.scenario_2_files)
        missing_item = next(
            item for item in report.gap_items if item.status == StatusEnum.MISSING
        )
        gen_output = self.orchestrator.trigger_generation(
            target_type="recommendation_letter", gap_item=missing_item
        )
        self.assertIsNotNone(gen_output.generated_text)
        self.assertEqual(gen_output.doc_type, "recommendation_letter")


if __name__ == "__main__":
    unittest.main()