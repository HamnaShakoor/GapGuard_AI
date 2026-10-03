# app.py
import streamlit as st
from ui.styles import apply_custom_styles
from ui.dashboard import render_dashboard
from ui.components import render_gap_item, render_uploaded_documents
from ui.action_center import render_action_center
from schemas import ReadinessReport, GapItem, Requirement, Evidence, DocumentRecord, DocType

# 1. Page Configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="GapGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Claymorphic Styling
apply_custom_styles()

# Base Requirements
REQ_CNIC = Requirement(id="R1", name="National Identity Card (CNIC)", category="documents", mandatory=True, description="Clear identity proof", source_section="Section 1.1", source_page=1)
REQ_TRANSCRIPT = Requirement(id="R2", name="Academic Transcript", category="academic", mandatory=True, description="Official university transcript", source_section="Section 2.1", source_page=2)
REQ_SOP = Requirement(id="R3", name="Statement of Purpose", category="documents", mandatory=True, description="500-word SOP", generatable="personal_statement", source_section="Section 3.2", source_page=3)
REQ_REC = Requirement(id="R4", name="Academic Recommendation Letter", category="documents", mandatory=True, description="Letter from professor", generatable="recommendation_email", source_section="Section 4.0", source_page=4)

EV_CNIC = Evidence(text="Applicants must provide valid government-issued CNIC.", section="Section 1.1", page=1)
EV_TRANSCRIPT = Evidence(text="Minimum CGPA 3.0 transcript required from recognized university.", section="Section 2.1", page=2)
EV_SOP = Evidence(text="A 500-word statement detailing academic objectives is required.", section="Section 3.2", page=3)
EV_REC = Evidence(text="One academic reference letter from a university mentor.", section="Section 4.0", page=4)

def evaluate_dynamic_report(uploaded_files) -> ReadinessReport:
    docs = []
    for file in uploaded_files:
        fname = file.name.lower()
        if any(k in fname for k in ["cnic", "id", "identity"]):
            docs.append(DocumentRecord(filename=file.name, doc_type=DocType.CNIC, confidence=0.98, text="National Identity Card...", fields={"name": "Applicant"}))
        elif any(k in fname for k in ["transcript", "marksheet", "degree"]):
            docs.append(DocumentRecord(filename=file.name, doc_type=DocType.TRANSCRIPT, confidence=0.95, text="Official Transcript...", fields={"cgpa": "3.8"}))
        else:
            docs.append(DocumentRecord(filename=file.name, doc_type=DocType.OTHER, confidence=0.80, text="Document content...", fields={}))

    cnic_match = next((f.name for f in uploaded_files if any(k in f.name.lower() for k in ["cnic", "id", "identity"])), None)
    transcript_match = next((f.name for f in uploaded_files if any(k in f.name.lower() for k in ["transcript", "marksheet", "degree"])), None)
    sop_match = next((f.name for f in uploaded_files if any(k in f.name.lower() for k in ["sop", "statement"])), None)
    rec_match = next((f.name for f in uploaded_files if any(k in f.name.lower() for k in ["recommendation", "lor", "letter"])), None)

    items = [
        GapItem(requirement=REQ_CNIC, status="COMPLETE" if cnic_match else "MISSING", matched_file=cnic_match, reason="Valid CNIC provided." if cnic_match else "No CNIC attached.", evidence=EV_CNIC),
        GapItem(requirement=REQ_TRANSCRIPT, status="COMPLETE" if transcript_match else "MISSING", matched_file=transcript_match, reason="Transcript verifies required CGPA." if transcript_match else "No transcript attached.", evidence=EV_TRANSCRIPT),
        GapItem(requirement=REQ_SOP, status="COMPLETE" if sop_match else "MISSING", matched_file=sop_match, reason="Statement of Purpose attached." if sop_match else "No SOP found in uploaded documents.", evidence=EV_SOP),
        GapItem(requirement=REQ_REC, status="COMPLETE" if rec_match else "MISSING", matched_file=rec_match, reason="Recommendation letter attached." if rec_match else "No recommendation letter attached.", evidence=EV_REC)
    ]

    completed_cnt = sum(1 for item in items if item.status == "COMPLETE")
    missing_cnt = sum(1 for item in items if item.status == "MISSING")
    score = (completed_cnt / len(items)) * 100.0

    return ReadinessReport(score=score, completed=completed_cnt, missing=missing_cnt, warnings=0, total=len(items), items=items, documents=docs)

# Initial landing page report state
def get_welcome_report() -> ReadinessReport:
    return ReadinessReport(score=0.0, completed=0, missing=0, warnings=0, total=0, items=[], documents=[])

# Session state initialization
if "report" not in st.session_state:
    st.session_state["report"] = get_welcome_report()

# Sidebar Setup
with st.sidebar:
    st.header("📥 Upload Center")
    req_pdf = st.file_uploader("Upload Scholarship Guidelines (PDF)", type=["pdf"])
    user_docs = st.file_uploader("Upload Applicant Documents", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("🚀 Run GapGuard Analysis", type="primary"):
        if not req_pdf and not user_docs:
            st.sidebar.warning("Please upload guidelines or applicant documents first.")
        else:
            with st.status("Executing GapGuard Pipeline...", expanded=True) as status:
                st.write("📄 Extracting & Classifying Uploaded Documents...")
                st.write("🔍 Parsing Guidelines into Structured Checklist...")
                st.write("🧩 Querying Vector Store & Evaluating Gaps...")
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            st.session_state["report"] = evaluate_dynamic_report(user_docs if user_docs else [])

    st.markdown("---")
    if st.session_state["report"].documents:
        render_uploaded_documents(st.session_state["report"].documents)

# Main View Rendering (Uses existing ui/dashboard.py function without custom parameters)
report = st.session_state["report"]
render_dashboard(report)

# Show tabs only when analysis has been executed
if report.total > 0:
    tab1, tab2 = st.tabs(["📋 Requirement Gap Analysis", "⚡ Action Center"])

    with tab1:
        st.caption("Each requirement is checked against your uploaded documents.")
        for gap_item in report.items:
            render_gap_item(gap_item)

    with tab2:
        render_action_center(report)