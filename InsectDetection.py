import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Detection | TSA 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Initialize Session State ───────────────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "reset_confirmed" not in st.session_state:
    st.session_state.reset_confirmed = False

# ── Color Palettes ────────────────────────────────────────
EARTH_BROWN = "#3B2F2F"
DARK_PALETTE = {
    "BG": "#121412",
    "CARD": "#26221C",
    "SURFACE": "#1A1916",
    "TEXT": "#E0E4E0",
    "TEXT_DIM": "#8AA38D",
    "ACCENT": "#4CAF50",
    "BORDER": "#3D362E"
}
LIGHT_PALETTE = {
    "BG": "#F4F7F4",
    "CARD": "#F5E6D3",
    "SURFACE": "#EEEDE8",
    "TEXT": "#1B2E1B",
    "TEXT_DIM": "#5D574F",
    "ACCENT": "#2E8B57",
    "BORDER": "#D9C5B2"
}

colors = DARK_PALETTE if st.session_state.dark_mode else LIGHT_PALETTE
BG, CARD, SURFACE, TEXT, TEXT_DIM, ACCENT, BORDER = (
    colors["BG"], colors["CARD"], colors["SURFACE"], colors["TEXT"], colors["TEXT_DIM"], colors["ACCENT"], colors["BORDER"]
)

# ── CSS Overrides (Premium Typography & Buttons) ──────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    /* === GLOBAL FONTS === */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"], .stButton button, p, span, div {{ 
        font-family: 'Inter', sans-serif !important;
    }}

    .main {{ background-color: {BG} !important; }}

    /* === PREMIUM BUTTONS (Fixes Clear Data font) === */
    .stButton > button {{
        border-radius: 12px !important;
        border: 1px solid {BORDER} !important;
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stButton > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
        background-color: {CARD} !important;
        transform: translateY(-1px);
    }}

    /* === BENTO CARDS === */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 20px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    /* === TYPOGRAPHY === */
    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 1.8px; 
        font-size: 0.65rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
        opacity: 0.9;
    }}

    /* === LIVE BADGE === */
    .live-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {ACCENT}15;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid {ACCENT}33;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}77; }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 6px {ACCENT}00; }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}00; }}
    }}
    .dot {{ height: 8px; width: 8px; background-color: {ACCENT}; border-radius: 50%; animation: pulse 2s infinite; }}

    /* === INPUTS & SLIDERS === */
    div[data-baseweb="input"] {{ background-color: {SURFACE} !important; border-radius: 10px !important; border: 1px solid {BORDER} !important; }}
    div[role="slider"] {{ background-color: {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt') 

model = load_model()

def classify(img):
    # Simulated prediction for UI display
    return "Stink Bug", 0.92

# ── Header ────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])

with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display, serif !important; color:{TEXT}; margin:0; font-size:2.8rem;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="eyebrow" style="color:{TEXT_DIM}; margin-top:-5px;">Engineering Design Portfolio | TSA 2026</p>', unsafe_allow_html=True)

with h_col2:
    theme_label = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    tabs = st.tabs(["Camera Control", "Manual Upload"])
    
    with tabs[0]:
        st.markdown(f"""<div class="live-badge"><div class="dot"></div><span style="color:{ACCENT}; font-size:0.7rem; font-weight:800; letter-spacing:0.5px;">LIVE SYSTEM ACTIVE</span></div>""", unsafe_allow_html=True)
        st.write("")
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            img = PIL.Image.open(cam_image)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Upload Specimen Image", type=["jpg","png"])
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Initialize Vision Engine", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Control Panel</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        is_custom = st.toggle("Custom Alert Email", value=False)
        target_email = st.text_input("Recipient", value="agiridhar41@gmail.com") if is_custom else "agiridhar41@gmail.com"
        
        st.markdown(f"<p class='eyebrow' style='margin-top:20px; color:{TEXT_DIM}; font-size:0.6rem;'>Alert Threshold</p>", unsafe_allow_html=True)
        current_threshold = st.slider("Threshold", 1, 50, 5, label_visibility="collapsed")
        
        st.write("")
        if st.button("Clear Data", use_container_width=True):
            st.session_state.inventory = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Intelligence Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow" style="color:{TEXT_DIM}; font-size:0.6rem;">Recent Classification</p>
            <div style="font-family:'Playfair Display', serif !important; font-size: 2.2rem; color:{TEXT};">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px; align-items:center; background:{SURFACE}; padding:10px; border-radius:12px;">
                <span style="color:{TEXT_DIM}; font-size:0.75rem; font-weight:600;">CONFIDENCE</span>
                <span style="color:{ACCENT}; font-weight:800; font-size:1.1rem;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="text-align:center; border-top:1px solid {BORDER}; padding-top:20px;">
        <p style="color:{ACCENT}; font-weight:800; letter-spacing:2px; font-size:0.7rem; margin:0;">ENGINEERING DESIGN</p>
        <p style="color:{TEXT_DIM}; font-size:0.7rem; font-weight:500; margin-top:5px;">TEAM ID: 2043-901 | TSA 2026</p>
    </div>
""", unsafe_allow_html=True)
