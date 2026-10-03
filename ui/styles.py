# ui/styles.py  -- Soft lavender clay theme
import streamlit as st

CLAY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* ============================================================
   0. TOKENS
   ============================================================ */
:root {
    --bg-a:        #E6DFF8;
    --bg-b:        #F4EFFC;
    --panel:       #FBF8FF;
    --card:        #FFFFFF;
    --purple-400:  #A596F0;
    --purple-500:  #8B7BE8;
    --purple-600:  #7060D8;
    --purple-700:  #4C3FA8;
    --ink:         #2B2257;
    --muted:       #6B6490;
    --yellow:      #FDE047;
    --yellow-hov:  #EAB308;

    --puff:     10px 10px 24px rgba(112, 96, 216, 0.14), -8px -8px 20px rgba(255, 255, 255, 0.95),
                inset 0 2px 0 rgba(255, 255, 255, 0.9);
    --puff-hov: 14px 14px 28px rgba(112, 96, 216, 0.20), -8px -8px 20px rgba(255, 255, 255, 1),
                inset 0 2px 0 rgba(255, 255, 255, 0.9);
    --puff-sm:  5px 5px 12px rgba(112, 96, 216, 0.12), -4px -4px 10px rgba(255, 255, 255, 0.95);
    --inset:    inset 3px 3px 8px rgba(112, 96, 216, 0.12), inset -3px -3px 8px rgba(255, 255, 255, 0.95);
}

/* ============================================================
   1. CANVAS + MAIN PANEL
   ============================================================ */
.stApp {
    background: linear-gradient(160deg, var(--bg-a) 0%, var(--bg-b) 100%) !important;
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--ink);
}
.stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea, .stApp button, .stApp summary {
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
header[data-testid="stHeader"] { background: transparent !important; }

/* The whole main area becomes one big soft panel, like the reference */
.block-container {
    background: var(--panel);
    border-radius: 36px;
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    margin-top: 1rem;
    margin-bottom: 2rem;
    max-width: 1180px;
    box-shadow: 0 24px 60px rgba(112, 96, 216, 0.18), inset 0 2px 0 rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.8);
}
.stApp h2, .stApp h3, .stApp h4 {
    color: var(--ink) !important;
    font-weight: 800 !important;
    letter-spacing: -0.2px;
}
.stApp [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

/* ============================================================
   2. HERO BANNER  (mascot + greeting)
   ============================================================ */
.hero-banner {
    display: flex;
    align-items: center;
    gap: 28px;
    background: linear-gradient(135deg, #D3C9F8 0%, #B7A8F2 100%);
    border-radius: 28px;
    padding: 24px 34px;
    margin-bottom: 26px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 14px 30px rgba(112, 96, 216, 0.25),
                inset 0 2px 0 rgba(255, 255, 255, 0.6),
                inset 0 -8px 16px rgba(112, 96, 216, 0.18);
}
.hero-mascot { flex: 0 0 auto; filter: drop-shadow(0 10px 10px rgba(76, 63, 168, 0.28)); }
.hero-mascot svg { width: 104px; height: auto; display: block; }
.hero-text { min-width: 0; }
.stApp .hero-banner h1 {
    color: var(--ink) !important;
    font-weight: 900 !important;
    font-size: 1.9rem !important;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0 !important;
    padding: 0 !important;
    line-height: 1.15 !important;
}
.stApp .hero-banner p {
    color: var(--purple-700) !important;
    margin: 0 0 14px 0 !important;
    font-size: 1rem;
    font-weight: 600;
}
.hero-chip {
    display: inline-block;
    background: #FFFDFB;
    color: var(--purple-700);
    font-weight: 800;
    font-size: 0.88rem;
    padding: 8px 18px;
    border-radius: 9999px;
    box-shadow: var(--puff-sm);
}

/* ============================================================
   3. STAT CARDS  (pastel-tinted, icon tile, big number)
   ============================================================ */
.stat-card, .metric-card, [data-testid="stMetric"] {
    border-radius: 24px !important;
    box-shadow: var(--puff) !important;
    border: 1px solid rgba(255, 255, 255, 0.7) !important;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.stat-card { padding: 18px 20px; }
.stat-card:hover, [data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: var(--puff-hov) !important; }
[data-testid="stMetric"] { background: var(--card) !important; padding: 18px 20px !important; }

.tone-lavender { background: linear-gradient(145deg, #EEE8FF, #DFD5FB); }
.tone-mint     { background: linear-gradient(145deg, #E0F8EC, #CDF0DE); }
.tone-coral    { background: linear-gradient(145deg, #FFE7E2, #FFD3CC); }
.tone-butter   { background: linear-gradient(145deg, #FFF6D2, #FFEBA8); }

.stat-top { display: flex; align-items: center; gap: 10px; }
.stat-icon {
    width: 34px; height: 34px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    color: #FFFFFF; font-weight: 900; font-size: 1rem;
    box-shadow: 0 4px 8px rgba(43, 34, 87, 0.18), inset 0 2px 0 rgba(255, 255, 255, 0.35);
}
.icon-lavender { background: #8B7BE8; }
.icon-mint     { background: #2FBF8A; }
.icon-coral    { background: #F0706A; }
.icon-butter   { background: #F2B01E; }

.stat-card .lbl, [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
    font-size: 0.9rem !important; font-weight: 800 !important; color: var(--muted) !important;
}
.stat-card .val, [data-testid="stMetricValue"] {
    font-size: 2.2rem !important; font-weight: 900 !important;
    color: var(--ink) !important; line-height: 1.1; margin: 10px 0 2px 0;
}
.stat-card .sub { font-size: 0.8rem; font-weight: 700; color: var(--muted); }

[data-testid="stProgress"] [data-baseweb="progress-bar"] > div {
    background-color: #E6DFF8 !important; border-radius: 999px !important;
    height: 12px !important; box-shadow: var(--inset);
}
[data-testid="stProgress"] [data-baseweb="progress-bar"] > div > div {
    background: linear-gradient(90deg, #8B7BE8, #B79CF5) !important; border-radius: 999px !important;
}

/* ============================================================
   4. REQUIREMENT CARDS
   ============================================================ */
.gap-card {
    display: flex; gap: 18px; align-items: flex-start;
    background: var(--card);
    border-radius: 24px;
    padding: 20px 24px;
    margin-bottom: 8px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: var(--puff);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.gap-card:hover { transform: translateY(-2px); box-shadow: var(--puff-hov); }
.gap-icon {
    flex: 0 0 auto; width: 44px; height: 44px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 900; font-size: 1.25rem;
    box-shadow: 0 5px 10px rgba(43, 34, 87, 0.18), inset 0 2px 0 rgba(255, 255, 255, 0.35);
}
.status-complete .gap-icon { background: #2FBF8A; }
.status-missing  .gap-icon { background: #F0706A; }
.status-warning  .gap-icon { background: #F2B01E; }
.gap-body { min-width: 0; flex: 1; }
.gap-title { font-size: 1.1rem; font-weight: 800; color: var(--ink); margin: 2px 0 0 0; }
.gap-reason { margin: 6px 0 8px 0; color: #4A4373; font-size: 0.92rem; line-height: 1.5; font-weight: 600; }
.gap-meta { font-size: 0.78rem; color: var(--muted); font-weight: 700; }
.gap-meta code { background: #F1ECFD; color: var(--purple-700); padding: 2px 8px; border-radius: 8px; font-weight: 700; }

[data-testid="stExpander"] { border: none !important; background: transparent !important; margin-bottom: 22px; }
[data-testid="stExpander"] details {
    background: var(--card) !important;
    border: 1px solid rgba(255, 255, 255, 0.8) !important;
    border-radius: 20px !important;
    box-shadow: var(--puff-sm);
    color: var(--ink);
}
[data-testid="stExpander"] summary { color: var(--purple-700) !important; font-weight: 800; border-radius: 20px; }
[data-testid="stExpander"] p, [data-testid="stExpander"] span { color: var(--ink); }

/* ============================================================
   5. PILLS
   ============================================================ */
.pill {
    display: inline-block; padding: 4px 13px; border-radius: 9999px;
    font-size: 0.68rem; font-weight: 900; letter-spacing: 0.6px; margin-right: 6px;
    text-transform: uppercase;
    box-shadow: 2px 2px 5px rgba(112, 96, 216, 0.08), inset 1px 1px 2px rgba(255, 255, 255, 0.7);
}
.pill-complete  { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
.pill-missing   { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
.pill-warning   { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.pill-mandatory { background: #E0E7FF; color: #1E40AF; border: 1px solid #C7D2FE; }
.pill-optional  { background: #F1ECFD; color: var(--muted); border: 1px solid #E3DAF8; }

/* ============================================================
   6. TABS  -> segmented pill tray, active = solid purple
   ============================================================ */
[data-baseweb="tab-list"] {
    gap: 6px !important; padding: 6px !important;
    background: #EFE9FC !important; border-radius: 9999px;
    width: fit-content; box-shadow: var(--inset); margin-bottom: 18px;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }
button[data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    border-radius: 9999px !important; padding: 10px 24px !important; height: auto !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
button[data-baseweb="tab"] p { color: var(--purple-700) !important; font-weight: 800 !important; font-size: 0.95rem !important; margin: 0 !important; }
button[data-baseweb="tab"]:hover { background: rgba(255, 255, 255, 0.7) !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(145deg, #9A8AEA, #7060D8) !important;
    box-shadow: 5px 5px 12px rgba(112, 96, 216, 0.35), inset 0 2px 0 rgba(255, 255, 255, 0.35);
}
button[data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF !important; }

/* ============================================================
   7. SIDEBAR  (rounded purple panel + ivory upload cards)
   ============================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #A99BF0 0%, #8878E4 100%) !important;
    border-radius: 0 32px 32px 0;
    box-shadow: 10px 0 30px rgba(112, 96, 216, 0.25);
    border-right: none;
}
section[data-testid="stSidebar"] > div { background: transparent !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-weight: 900 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.35) !important; }

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--card);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 22px; padding: 14px; margin-bottom: 14px;
    box-shadow: 6px 6px 14px rgba(43, 34, 87, 0.18), -3px -3px 8px rgba(255, 255, 255, 0.25);
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--ink) !important; font-weight: 800; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: #F7F3FF !important;
    border: 2px dashed #B9ABF2 !important;
    border-radius: 16px !important;
    box-shadow: inset 2px 2px 6px rgba(112, 96, 216, 0.08);
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div { color: var(--muted) !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background: var(--purple-500) !important; color: #fff !important; border: none !important;
    font-weight: 800 !important; border-radius: 12px !important;
    box-shadow: 3px 3px 8px rgba(112, 96, 216, 0.35) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover { background: var(--purple-600) !important; }

.sidebar-card {
    background: var(--card); border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 18px; padding: 12px 16px; margin-bottom: 12px;
    box-shadow: 5px 5px 12px rgba(43, 34, 87, 0.16);
}
.sidebar-card .fname { font-weight: 800; font-size: 0.84rem; color: var(--ink); word-break: break-all; }
.sidebar-card .meta  { font-size: 0.74rem; color: var(--muted); margin-top: 4px; font-weight: 700; }
.sidebar-card .meta b.type { color: var(--purple-700); }
.sidebar-card .meta b.conf { color: #1B8F63; }

/* ============================================================
   8. BUTTONS
   ============================================================ */
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: linear-gradient(145deg, #FFE866, #FDE047) !important;
    color: var(--ink) !important; font-weight: 900 !important; font-size: 0.95rem !important;
    border: 1px solid rgba(234, 179, 8, 0.5) !important; border-radius: 9999px !important;
    padding: 12px 24px !important; width: 100% !important;
    box-shadow: 6px 6px 14px rgba(43, 34, 87, 0.20), -3px -3px 8px rgba(255, 255, 255, 0.35),
                inset 0 2px 0 rgba(255, 255, 255, 0.8) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button[kind="primary"] p, [data-testid="stBaseButton-primary"] p { color: var(--ink) !important; font-weight: 900 !important; }
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background: var(--yellow-hov) !important; color: var(--ink) !important; transform: translateY(-2px);
}
.stButton > button[kind="primary"]:active, [data-testid="stBaseButton-primary"]:active {
    transform: translateY(1px); box-shadow: inset 3px 3px 6px rgba(43, 34, 87, 0.25) !important;
}

/* Secondary + download: purple clay pills */
.stButton > button[kind="secondary"], [data-testid="stBaseButton-secondary"], [data-testid="stDownloadButton"] button {
    background: linear-gradient(145deg, #9A8AEA, #7C6BE0) !important;
    color: #FFFFFF !important; border: none !important; border-radius: 9999px !important;
    font-weight: 800 !important; padding: 8px 20px !important;
    box-shadow: 5px 5px 12px rgba(112, 96, 216, 0.32), inset 0 2px 0 rgba(255, 255, 255, 0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"] p, [data-testid="stBaseButton-secondary"] p, [data-testid="stDownloadButton"] button p { color: #fff !important; }
.stButton > button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(145deg, #8B7BE8, #6A59D4) !important; transform: translateY(-1px);
}

/* ============================================================
   9. FORMS / ALERTS
   ============================================================ */
[data-testid="stTextArea"] textarea {
    background: var(--card) !important; color: var(--ink) !important;
    border: 1px solid rgba(112, 96, 216, 0.10) !important; border-radius: 18px !important; box-shadow: var(--inset);
}
[data-testid="stAlert"] { border-radius: 18px !important; border: 1px solid rgba(255, 255, 255, 0.8) !important; box-shadow: var(--puff-sm); }
hr { border-color: rgba(112, 96, 216, 0.12) !important; }

/* ============================================================
   10. ACCESSIBILITY + MOBILE
   ============================================================ */
button:focus-visible, [data-baseweb="tab"]:focus-visible { outline: 3px solid rgba(112, 96, 216, 0.55) !important; outline-offset: 2px; }
@media (max-width: 760px) {
    .block-container { border-radius: 24px; padding: 1.2rem 1rem 2rem 1rem !important; }
    .hero-banner { flex-direction: column; text-align: center; padding: 22px; }
}
@media (prefers-reduced-motion: reduce) {
    .stat-card, .gap-card, button, [data-testid="stMetric"] { transition: none !important; transform: none !important; }
}
</style>
"""


def apply_custom_styles():
    st.markdown(CLAY_CSS, unsafe_allow_html=True)