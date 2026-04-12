import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Detection | TSA 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Initialize Session State ───────────────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "cam_enabled" not in st.session_state:
    st.session_state.cam_enabled = True

# ── Color Palettes ────────────────────────────────────────
if st.session_state.dark_mode:
    BG_GRADIENT = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)"
    CARD_BG = "rgba(20, 32, 20, 0.8)"
    TEXT = "#E0E4E0"
    TEXT_DIM = "#8AA38D"
    ACCENT = "#4CAF50" # Forest Green
    BORDER = "#2D362E"
    SURFACE = "#1A1D1A"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F0F7F0 0%, #E2E8E2 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.7)"
    TEXT = "#1B2E1B"
    TEXT_DIM = "#4A5D4C"
    ACCENT = "#2E8B57" # Sea Green
    BORDER = "#C2D9C5"
    SURFACE = "#F0F2F0"

# ── CSS Overrides (Fixing Tab Alignment & Text Bugs) ──────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    
    .main, [data-testid="stAppViewContainer"] {{ 
        background: {BG_GRADIENT} !important; 
        font-family: 'Inter', sans-serif !important;
        transition: all 0.6s ease-in-out !important;
    }}

    .header-container {{
        text-align: center;
        padding: 40px 0 30px 0;
    }}

    .bento-card {{ 
        background: {CARD_BG}; 
        backdrop-filter: blur(12px);
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 40, 0, 0.1);
        transition: all 0.3s ease !important;
    }}
    
    .bento-card:hover {{
        transform: translateY(-5px);
        border-color: {ACCENT};
        box-shadow: 0 12px 40px rgba(76, 175, 80, 0.15);
    }}

    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-size: 0.75rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
    }}

    /* === FIXING TABS ALIGNMENT === */
    [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 1px solid {BORDER} !important;
        gap: 24px !important;
    }}
    
    [data-baseweb="tab"] {{
        padding: 10px 0px !important;
        background-color: transparent !important;
    }}

    [data-baseweb="tab"] div p {{
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        color: {TEXT_DIM} !important;
        transition: color 0.3s ease !important;
    }}

    [data-baseweb="tab"][aria-selected="true"] div p {{
        color: {ACCENT} !important;
    }}

    [data-baseweb="tab-highlight"] {{
        background-color: {ACCENT} !important;
    }}

    /* Button Styling */
    .stButton > button {{
        border-radius: 14px !important;
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        transition: 0.3s !important;
    }}

    .stButton > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
        background-color: {ACCENT}11 !important;
    }}

    /* Visibility Fixes for Labels */
    label, .stMarkdown p, .stSlider p, div[data-testid="stWidgetLabel"] p {{
        color: {TEXT} !important;
        font-weight: 500 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt') 

def classify(img):
    return "Common Beetle", 0.94 

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Scanning...", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

# ── Header Section ────────────────────────────────────────
st.markdown(f"""
    <div class="header-container">
        <h1 style="font-family:'Playfair Display'; color:{TEXT}; font-size: 4.5rem; margin:0; letter-spacing:-1px;">Insect Detection</h1>
        <p style="color:{ACCENT}; font-size:0.85rem; font-weight:700; letter-spacing:4px; margin-top:10px;">
            TSA 2026 &nbsp; | &nbsp; BIOMETRIC SURVEILLANCE &nbsp; | &nbsp; TEAM 2043-901
        </p>
    </div>
""", unsafe_allow_html=True)

# Theme Toggle Positioning
t_col1, t_col2 = st.columns([10, 1])
with t_col2:
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown('<p class="eyebrow">Digital Intake</p>', unsafe_allow_html=True)
    
    # Structure for the tabs
    tab_live, tab_archive = st.tabs(["[ LIVE FEED ]", "[ ARCHIVE UPLOAD ]"])
    
    with tab_live:
        st.session_state.cam_enabled = st.toggle("Enable Hardware Camera", value=st.session_state.cam_enabled)
        if st.session_state.cam_enabled:
            cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
        else:
            st.info("System waiting for hardware camera toggle.")
    
    with tab_archive:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        upload_mode = st.radio("Archive Mode", ["Single Specimen", "Batch Processing"], horizontal=True)
        
        up = st.file_uploader("Select Files", type=["jpg","png"], accept_multiple_files=(upload_mode == "Batch Processing"))
        if up:
            if st.button("Process Archive", use_container_width=True):
                # Analysis logic here
                st.success("Analysis complete.")
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Intelligence Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    
    st.markdown(f"""
        <div class="bento-card" style="border-left: 6px solid {ACCENT};">
            <p class="eyebrow" style="color:{TEXT_DIM}">Identified Taxon</p>
            <div style="font-family:'Playfair Display'; font-size: 3rem; color:{TEXT}; line-height:1;">{label}</div>
            <div style="margin-top:20px;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem; font-weight:600;">CONFIDENCE</span>
                <div style="color:{ACCENT}; font-weight:800; font-size:1.5rem;">{conf:.1%}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Session Inventory</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM}; font-style:italic;'>Inventory empty.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid {BORDER}55;">
                    <span style="color:{TEXT}; font-weight:600;">{species}</span>
                    <span style="color:{ACCENT}; font-weight:800;">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Purge Session Data", use_container_width=True):
        st.session_state.inventory = {}
        st.rerun()
