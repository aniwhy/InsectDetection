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
if "cam_on" not in st.session_state:
    st.session_state.cam_on = True

# ── Color Palettes ────────────────────────────────────────
DARK_PALETTE = {
    "BG": "#121412", "CARD": "#26221C", "SURFACE": "#1A1916",
    "TEXT": "#E0E4E0", "TEXT_DIM": "#8AA38D", "ACCENT": "#4CAF50", "BORDER": "#3D362E"
}
LIGHT_PALETTE = {
    "BG": "#F4F7F4", "CARD": "#F5E6D3", "SURFACE": "#EEEDE8",
    "TEXT": "#1B2E1B", "TEXT_DIM": "#5D574F", "ACCENT": "#2E8B57", "BORDER": "#D9C5B2"
}

colors = DARK_PALETTE if st.session_state.dark_mode else LIGHT_PALETTE
BG, CARD, SURFACE, TEXT, TEXT_DIM, ACCENT, BORDER = (
    colors["BG"], colors["CARD"], colors["SURFACE"], colors["TEXT"], colors["TEXT_DIM"], colors["ACCENT"], colors["BORDER"]
)

# ── CSS Overrides (Premium Fonts & Bento Style) ────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"], p, span, div, label {{ 
        font-family: 'Inter', sans-serif !important; 
    }}
    .main {{ background-color: {BG} !important; }}

    .bento-card {{ 
        background: {CARD}; border: 1px solid {BORDER}; 
        border-radius: 20px; padding: 24px; margin-bottom: 20px;
        transition: all 0.3s ease;
    }}

    .eyebrow {{ 
        text-transform: uppercase; letter-spacing: 1.5px; 
        font-size: 0.7rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px;
    }}

    .stButton > button {{
        font-family: 'Inter', sans-serif !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

model = load_model()

def classify(img):
    # Simulated prediction
    return "Common Beetle", 0.94

def add_to_inventory(label):
    if label not in ["Scanning...", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1

# ── Header ────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin:0;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="eyebrow" style="color:{TEXT_DIM}; margin-top:-5px;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)

with h_col2:
    if st.button("☀️" if st.session_state.dark_mode else "🌙", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    
    # Camera Controls
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        cam_toggle = st.toggle("Enable Camera", value=st.session_state.cam_on)
    with c_col2:
        auto_sync = st.toggle("Auto-Sync (3s)", value=False)

    tabs = st.tabs(["Camera Feed", "Manual Upload"])
    
    with tabs[0]:
        if cam_toggle:
            cam_placeholder = st.empty()
            cam_image = cam_placeholder.camera_input("Snapshot", label_visibility="collapsed")
            
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
                
                if auto_sync:
                    time.sleep(3)
                    st.rerun()
        else:
            st.info("Camera is currently disabled.")

    with tabs[1]:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Upload Image", type=["jpg","png"])
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Analyze Specimen", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">System Configuration</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        target_email = st.text_input("Recipient", value="agiridhar41@gmail.com")
        current_threshold = st.slider("Population Threshold", 1, 50, 5)
        
        if st.button("Clear Data", use_container_width=True):
            st.session_state.inventory = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Intelligence Engine Display
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow" style="color:{TEXT_DIM}">Latest Detection</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:700;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Inventory Tracker
    st.markdown(f'<div class="bento-card"><p class="eyebrow">Population Tracker</p>', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.9rem;'>No records found.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid {BORDER}55;">
                    <span style="color:{TEXT}; font-weight:500;">{species}</span>
                    <span style="color:{ACCENT}; font-weight:700;">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Engineering Design Footer ──────────────────────────────
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; border-top:1px solid {BORDER}; padding-top:20px;">
        <p style="color:{ACCENT}; font-weight:800; letter-spacing:2px; font-size:0.7rem; margin:0;">ENGINEERING DESIGN</p>
        <p style="color:{TEXT_DIM}; font-size:0.7rem; font-weight:500; margin-top:5px;">TEAM ID: 2043-901 | TSA 2026</p>
    </div>
""", unsafe_allow_html=True)
