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

# Use the team's real backend if orchestrator.py exists, otherwise demo data
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
    """Demo data. Uses exactly the same fields/values as the original working mock."""
    types = [DocType.CNIC, DocType.TRANSCRIPT]
    docs = [
        DocumentRecord(filename=f.name, doc_type=types[i % 2], confidence=0.95, text="", fields={})
        for i, f in enumerate(user_docs or [])
    ]
    name1 = docs[0].filename if docs else "CNIC_Front.pdf"
    name2 = docs[1].filename if len(docs) > 1 else "BS_Transcript.pdf"

    req1 = Requirement(id="R1", name="National Identity Card (CNIC)", category="documents", mandatory=True,
                       description="Clear identity proof", source_section="Section 1.1", source_page=1)
    req2 = Requirement(id="R2", name="Academic Transcript", category="academic", mandatory=True,
                       description="Official university transcript", source_section="Section 2.1", source_page=2)
    req3 = Requirement(id="R3", name="Statement of Purpose", category="documents", mandatory=True,
                       description="500-word SOP", generatable="personal_statement",
                       source_section="Section 3.2", source_page=3)
    req4 = Requirement(id="R4", name="Academic Recommendation Letter", category="documents", mandatory=True,
                       description="Letter from professor", generatable="recommendation_email",
                       source_section="Section 4.0", source_page=4)

    ev1 = Evidence(text="Applicants must provide valid government-issued CNIC.", section="Section 1.1", page=1)
    ev2 = Evidence(text="Minimum CGPA 3.0 transcript required.", section="Section 2.1", page=2)
    ev3 = Evidence(text="A 500-word statement is required.", section="Section 3.2", page=3)
    ev4 = Evidence(text="One academic reference letter is required.", section="Section 4.0", page=4)

    items = [
        GapItem(requirement=req1, status="COMPLETE", matched_file=name1, reason="Valid CNIC provided.", evidence=ev1),
        GapItem(requirement=req2, status="COMPLETE", matched_file=name2, reason="Transcript meets the threshold.", evidence=ev2),
        GapItem(requirement=req3, status="MISSING", matched_file=None, reason="No SOP found.", evidence=ev3),
        GapItem(requirement=req4, status="MISSING", matched_file=None, reason="No recommendation letter attached.", evidence=ev4),
    ]
    return ReadinessReport(score=50.0, completed=2, missing=2, warnings=0, total=4, items=items, documents=docs)


if "report" not in st.session_state:
    st.session_state["report"] = get_welcome_report()

with st.sidebar:
    st.header("📥 Upload Center")
    req_pdf = st.file_uploader("Upload Guidelines / Program Criteria (PDF)", type=["pdf"])
    user_docs = st.file_uploader("Upload Applicant / Submission Documents", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("🚀 Run GapGuard Analysis", type="primary"):
        if not req_pdf and not user_docs:
            st.warning("Please upload guidelines or applicant documents first.")
        else:
            with st.spinner("Analyzing documents with GapGuard AI agents..."):
                try:
                    if HAS_BACKEND:
                        st.session_state["report"] = run_orchestrator(req_pdf, user_docs)
                    else:
                        st.session_state["report"] = generate_sample_report(req_pdf, user_docs)
                    st.success("Analysis complete!")
                    if not HAS_BACKEND:
                        st.info("Demo mode: showing sample results while the backend is being integrated.")
                except Exception as e:
                    st.error(f"Analysis failed: {type(e).__name__}: {e}")

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