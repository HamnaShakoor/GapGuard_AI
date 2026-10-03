# ui/action_center.py
import streamlit as st
from schemas import ReadinessReport, GeneratedContent

def mock_generate_content(kind: str, req_id: str) -> GeneratedContent:
    if kind == "personal_statement":
        return GeneratedContent(
            kind="personal_statement",
            title="Draft Personal Statement",
            body="I am writing to express my strong interest in the scholarship. Having completed my BS in AI with high distinction, I have demonstrated leadership in projects like RAASTA AI.\n\n[INSERT SPECIFIC CAREER GOAL HERE]\n\nMy academic background in machine learning makes me an ideal candidate.",
            placeholders=["INSERT SPECIFIC CAREER GOAL HERE"]
        )
    else:
        return GeneratedContent(
            kind="recommendation_email",
            title="Recommendation Request Email",
            body="Dear Professor,\n\nI hope this email finds you well. I am applying for the National AI Excellence Scholarship 2026.\n\nAs you supervised my work on C++ systems, would you be willing to provide a recommendation letter focusing on my problem-solving skills?\n\nDeadline: [INSERT DEADLINE DATE HERE].\n\nBest regards,\nHamna Shakoor",
            placeholders=["INSERT DEADLINE DATE HERE"]
        )

def render_action_center(report: ReadinessReport):
    # Duplicate "⚡ Action Center" subheader removed (the tab label already says it)
    st.write("Generate missing application materials tailored strictly to extracted facts.")

    generatable_items = [
        item for item in report.items
        if item.requirement.generatable and item.status in ["MISSING", "WARNING"]
    ]

    if not generatable_items:
        st.success("All generatable requirements are already complete!")
        return

    for item in generatable_items:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{item.requirement.name}** ({item.status})")
            st.caption(f"Action: Generate {item.requirement.generatable.replace('_', ' ').title()}")
        with col2:
            if st.button("Generate", key=f"gen_{item.requirement.id}"):
                with st.spinner("Generating grounded response..."):
                    res = mock_generate_content(item.requirement.generatable, item.requirement.id)
                    st.session_state[f"generated_{item.requirement.id}"] = res

        if f"generated_{item.requirement.id}" in st.session_state:
            gen_res: GeneratedContent = st.session_state[f"generated_{item.requirement.id}"]
            st.info(f"**{gen_res.title}**")
            st.text_area("Content", value=gen_res.body, height=180, key=f"txt_{item.requirement.id}")

            if gen_res.placeholders:
                st.warning(f"⚠️ Requires user attention for missing facts: {', '.join(gen_res.placeholders)}")

            st.download_button(
                label="📥 Download Draft (.txt)",
                data=gen_res.body,
                file_name=f"{gen_res.kind}_{item.requirement.id}.txt",
                mime="text/plain",
                key=f"dl_{item.requirement.id}"
            )
            st.divider()