# National AI Excellence Scholarship 2026 - Readiness & Gap Analysis System

An end-to-end AI-powered document evaluation and gap-analysis pipeline that assesses student applications against official scholarship criteria, calculates readiness scores, and auto-generates missing application artifacts.

## Architecture & Team Division
- **Member 1 (RAG Lead):** Chunking, vector storage (ChromaDB), and retrieval filtering.
- **Member 2 (Doc Processing Lead):** PDF/DOCX text extraction, OCR fallback, and LLM classification.
- **Member 3 (Requirement & Gap Analysis Lead):** Criteria extraction, evidence matching, and scoring engine.
- **Member 4 (LLM & Generation Lead):** Pydantic/JSON LLM wrapper and auto-generation agent.
- **Member 5 (UI Lead):** Streamlit dashboard, action center, and live progress indicators.
- **Member 6 (Orchestration, Data & QA Lead):** Schemas, pipeline sequencing, synthetic data generation, integration testing, and documentation.

## Directory Structure
```text
.
├── .vscode/
│   └── settings.json
├── agents/
│   ├── __init__.py
│   └── orchestrator.py
├── data/
│   └── requirements/
│       └── scholarship_requirements_2026.pdf
├── docs/
│   ├── architecture.md
│   └── demo_script.md
├── sample_documents/
│   ├── scenario_1_complete/
│   ├── scenario_2_missing_docs/
│   └── scenario_3_warnings/
├── tests/
│   └── test_integration.py
├── README.md
├── requirementpdf.py
├── schemas.py
└── test_results.md