# ui/components.py
import streamlit as st
from schemas import GapItem, DocumentRecord
from typing import List

_GLYPH = {"complete": "✓", "missing": "!", "warning": "?"}


def render_gap_item(item: GapItem):
    status_key = item.status.lower()
    mandatory_label = "MANDATORY" if item.requirement.mandatory else "OPTIONAL"
    mandatory_key = "mandatory" if item.requirement.mandatory else "optional"

    st.markdown(f"""
        <div class="gap-card status-{status_key}">
            <div class="gap-icon">{_GLYPH.get(status_key, "•")}</div>
            <div class="gap-body">
                <div>
                    <span class="pill pill-{status_key}">{item.status}</span>
                    <span class="pill pill-{mandatory_key}">{mandatory_label}</span>
                    <span class="gap-meta">{item.requirement.category}</span>
                </div>
                <div class="gap-title">{item.requirement.name}</div>
                <p class="gap-reason">{item.reason}</p>
                <div class="gap-meta">Matched document: <code>{item.matched_file or 'None detected'}</code></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 View grounded citation & source evidence"):
        st.markdown(f"**Guideline extract:** *\"{item.evidence.text}\"*")
        st.caption(f"📍 **Document citation:** {item.evidence.section} (Page {item.evidence.page})")


def render_uploaded_documents(documents: List[DocumentRecord]):
    st.sidebar.markdown("### 📄 Classified Documents")
    if not documents:
        st.sidebar.info("No documents uploaded yet.")
        return

    for doc in documents:
        st.sidebar.markdown(f"""
            <div class="sidebar-card">
                <div class="fname">{doc.filename}</div>
                <div class="meta">
                    Type: <b class="type">{doc.doc_type.value}</b> &nbsp;|&nbsp;
                    Confidence: <b class="conf">{doc.confidence*100:.0f}%</b>
                </div>
            </div>
        """, unsafe_allow_html=True)