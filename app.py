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
    """Mock analysis output to visualize the dashboard UI."""
    docs = []
    if req_pdf:
        docs.append(DocumentRecord(filename=req_pdf.name, doc_type=DocType.GUIDELINE, confidence=0.98))
    for doc in user_docs:
        docs.append(DocumentRecord(filename=doc.name, doc_type=DocType.APPLICANT, confidence=0.92))

    items = [
        GapItem(
            status="Complete",
            requirement=Requirement(name="Academic Transcripts", mandatory=True, category="Academics"),
            reason="Official transcript uploaded and verified.",
            matched_file=user_docs[0].name if user_docs else "transcript.pdf",
            evidence=Evidence(text="Transcript verified with GPA 3.8", section="Section 2.1", page=1)
        ),
        GapItem(
            status="Missing",
            requirement=Requirement(name="Letter of Recommendation", mandatory=True, category="Documents"),
            reason="No recommendation letter attached in the applicant bundle.",
            matched_file="",
            evidence=Evidence(text="Two reference letters required.", section="Section 4.0", page=3)
        ),
        GapItem(
            status="Warning",
            requirement=Requirement(name="Statement of Purpose", mandatory=False, category="Essays"),
            reason="Word count is slightly below recommended guidelines (450/500 words).",
            matched_file=user_docs[-1].name if len(user_docs) > 1 else "sop.pdf",
            evidence=Evidence(text="SOP should be between 500-1000 words.", section="Section 3.2", page=2)
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
    req_pdf = st.file_uploader("Upload Scholarship Guidelines (PDF)", type=["pdf"])
    user_docs = st.file_uploader("Upload Applicant Documents", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("🚀 Run GapGuard Analysis", type="primary"):
        if not req_pdf and not user_docs:
            st.warning("Please upload guidelines or applicant documents first.")
        else:
            with st.spinner("Analyzing documents with GapGuard AI agents..."):
                if HAS_BACKEND:
                    # Calls your team's real multi-agent pipeline
                    st.session_state["report"] = run_orchestrator(req_pdf, user_docs)
                else:
                    # Fallback UI visualization
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