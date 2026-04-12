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

# ── Color Palettes ────────────────────────────────────────
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

# ── CSS Overrides (Targeted Fix for Clear Data) ───────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    /* === GLOBAL FONTS === */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"], p, span, div {{ 
        font-family: 'Inter', sans-serif !important;
    }}

    .main {{ background-color: {BG} !important; }}

    /* === FIXED CLEAR DATA & PREMIUM BUTTONS === */
    .stButton > button {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 12px !important;
        border: 1px solid {BORDER} !important;
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }}
    .stButton > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
    }}

    /* === BENTO CARDS === */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 20px; 
        padding: 24px; 
        margin-bottom: 20px;
    }}

    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 1.8px; 
        font-size: 0.65rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin:0;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="eyebrow" style="color:{TEXT_DIM}; margin-top:-5px;">Engineering Design Portfolio</p>', unsafe_allow_html=True)

with h_col2:
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    # Camera/Upload logic goes here...
    st.markdown(f'<div class="bento-card" style="height: 300px; display: flex; align-items: center; justify-content: center; color: {TEXT_DIM};">System Awaiting Input</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Control Panel</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        st.text_input("Recipient Email", value="agiridhar41@gmail.com")
        st.write("")
        # The Fixed Button
        if st.button("Clear Data"):
            st.session_state.inventory = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="text-align:center; border-top:1px solid {BORDER}; padding-top:20px;">
        <p style="color:{ACCENT}; font-weight:800; letter-spacing:2px; font-size:0.7rem; margin:0;">ENGINEERING DESIGN</p>
        <p style="color:{TEXT_DIM}; font-size:0.7rem; font-weight:500; margin-top:5px;">TEAM ID: 2043-901 | TSA 2026</p>
    </div>
""", unsafe_allow_html=True)
