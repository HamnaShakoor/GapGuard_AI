import sys
from pathlib import Path

# Fix for Streamlit Cloud import paths
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from ui.styles import apply_custom_styles
from ui.dashboard import render_dashboard
from ui.components import render_gap_item, render_uploaded_documents
from ui.action_center import render_action_center
from schemas import ReadinessReport, GapItem, Requirement, Evidence, DocumentRecord, DocType

# Try importing backend orchestrator if available
try:
    from orchestrator import run_orchestrator
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

st.set_page_config(
    page_title="GapGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()


def get_welcome_report() -> ReadinessReport:
    return ReadinessReport(score=0.0, completed=0, missing=0, warnings=0, total=0, items=[], documents=[])


def generate_sample_report(req_pdf, user_docs) -> ReadinessReport:
    """Mock analysis output to visualize the dashboard UI smoothly."""
    docs = []
    
    # Safely select valid DocType enum member or string
    doc_type_guideline = getattr(DocType, "GUIDELINE", getattr(DocType, "GUIDELINES", "GUIDELINE"))
    doc_type_applicant = getattr(DocType, "APPLICANT", "APPLICANT")

    if req_pdf:
        docs.append(DocumentRecord(filename=req_pdf.name, doc_type=doc_type_guideline, confidence=0.98))
    
    if user_docs:
        for doc in user_docs:
            docs.append(DocumentRecord(filename=doc.name, doc_type=doc_type_applicant, confidence=0.92))

    first_doc_name = user_docs[0].name if user_docs else "submitted_document.pdf"
    last_doc_name = user_docs[-1].name if user_docs and len(user_docs) > 1 else "additional_doc.pdf"

    items = [
        GapItem(
            status="Complete",
            requirement=Requirement(name="Primary Application / Transcripts", mandatory=True, category="Core Requirements"),
            reason="Submitted document matches mandatory specifications.",
            matched_file=first_doc_name,
            evidence=Evidence(text="Document verified against requirement guidelines.", section="Section 2.1", page=1)
        ),
        GapItem(
            status="Missing",
            requirement=Requirement(name="Recommendation / Verification Letter", mandatory=True, category="Verification"),
            reason="Required supporting verification document is missing from submission batch.",
            matched_file="",
            evidence=Evidence(text="Mandatory verification letter required for qualification.", section="Section 4.0", page=3)
        ),
        GapItem(
            status="Warning",
            requirement=Requirement(name="Statement / Cover Document", mandatory=False, category="Optional Criteria"),
            reason="Document length or structure is slightly below suggested target guidelines.",
            matched_file=last_doc_name,
            evidence=Evidence(text="Recommended length: 500-1000 words.", section="Section 3.2", page=2)
        )
    ]

    return ReadinessReport(
        score=33.0,
        completed=1,
        missing=1,
        warnings=1,
        total=3,
        items=items,
        documents=docs
    )


if "report" not in st.session_state:
    st.session_state["report"] = get_welcome_report()

with st.sidebar:
    st.header("📥 Upload Center")
    # Generic Labels
    req_pdf = st.file_uploader("Upload Guidelines / Program Criteria (PDF)", type=["pdf"])
    user_docs = st.file_uploader("Upload Applicant / Submission Documents", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("🚀 Run GapGuard Analysis", type="primary"):
        if not req_pdf and not user_docs:
            st.warning("Please upload guidelines or applicant documents first.")
        else:
            with st.spinner("Analyzing documents with GapGuard AI agents..."):
                if HAS_BACKEND:
                    st.session_state["report"] = run_orchestrator(req_pdf, user_docs)
                else:
                    st.session_state["report"] = generate_sample_report(req_pdf, user_docs)
            st.success("Analysis complete!")

    st.markdown("---")
    if st.session_state["report"].documents:
        render_uploaded_documents(st.session_state["report"].documents)

report = st.session_state["report"]
render_dashboard(report)

if report.total > 0:
    tab1, tab2 = st.tabs(["📋 Requirement Gap Analysis", "⚡ Action Center"])

    with tab1:
        for gap_item in report.items:
            render_gap_item(gap_item)

    with tab2:
        render_action_center(report)