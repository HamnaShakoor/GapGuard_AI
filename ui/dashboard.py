# ui/dashboard.py
import streamlit as st
from schemas import ReadinessReport


def _mascot_svg(score: float) -> str:
    """Shield mascot whose mood follows the readiness score."""
    if score >= 75:
        mouth = '<path d="M46 82 Q60 98 74 82" fill="#FFFFFF" stroke="#2B2257" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
        extra = '<path d="M104 14 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3 z" fill="#FDE047"/>'
    elif score >= 40:
        mouth = '<path d="M49 85 Q60 93 71 85" fill="none" stroke="#2B2257" stroke-width="3.5" stroke-linecap="round"/>'
        extra = ""
    else:
        mouth = '<path d="M49 92 Q60 82 71 92" fill="none" stroke="#2B2257" stroke-width="3.5" stroke-linecap="round"/>'
        extra = '<path d="M98 40 q6 8 0 14 q-6 -6 0 -14 z" fill="#93C5FD"/>'
    return f"""
    <svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GapGuard shield mascot">
      <defs>
        <linearGradient id="gg-shield" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#A596F0"/><stop offset="1" stop-color="#6A59D4"/>
        </linearGradient>
      </defs>
      <path d="M60 8 L108 26 V68 C108 100 84 124 60 134 C36 124 12 100 12 68 V26 Z"
            fill="url(#gg-shield)" stroke="#FFFFFF" stroke-width="5" stroke-linejoin="round"/>
      <path d="M60 18 L98 32 V68 C98 92 80 112 60 122" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="5" stroke-linecap="round"/>
      <ellipse cx="45" cy="64" rx="5.5" ry="7" fill="#2B2257"/><ellipse cx="75" cy="64" rx="5.5" ry="7" fill="#2B2257"/>
      <circle cx="47" cy="61.5" r="2" fill="#FFFFFF"/><circle cx="77" cy="61.5" r="2" fill="#FFFFFF"/>
      <ellipse cx="34" cy="78" rx="7" ry="4.5" fill="#FF9FB5" fill-opacity="0.7"/>
      <ellipse cx="86" cy="78" rx="7" ry="4.5" fill="#FF9FB5" fill-opacity="0.7"/>
      {mouth}{extra}
    </svg>
    """


def _stat_card(tone: str, glyph: str, label: str, value: str, sub: str) -> str:
    return f"""
        <div class="stat-card tone-{tone}">
            <div class="stat-top">
                <div class="stat-icon icon-{tone}">{glyph}</div>
                <div class="lbl">{label}</div>
            </div>
            <div class="val">{value}</div>
            <div class="sub">{sub}</div>
        </div>
    """


def render_dashboard(report: ReadinessReport):
    # Friendly status line
    if report.missing == 0 and report.warnings == 0:
        chip = "You're ready to submit 🎉"
    else:
        left = report.missing + report.warnings
        chip = f"{left} thing{'s' if left != 1 else ''} left before you're ready to submit"

    # Single hero (the only H1 on the page)
    st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-mascot">{_mascot_svg(report.score)}</div>
            <div class="hero-text">
                <h1>GapGuard AI</h1>
                <p>Know what's missing before you submit.</p>
                <span class="hero-chip">{chip}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_stat_card("lavender", "%", "Readiness", f"{report.score:.0f}%", "of your checklist"), unsafe_allow_html=True)
    with c2:
        st.markdown(_stat_card("mint", "✓", "Completed", str(report.completed), f"of {report.total} requirements"), unsafe_allow_html=True)
    with c3:
        st.markdown(_stat_card("coral", "!", "Missing", str(report.missing), "need your attention"), unsafe_allow_html=True)
    with c4:
        st.markdown(_stat_card("butter", "?", "Warnings", str(report.warnings), "worth a second look"), unsafe_allow_html=True)

    st.write("")
    st.progress(report.score / 100.0)
    st.write("")