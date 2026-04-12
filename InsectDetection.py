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
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "cam_enabled" not in st.session_state:
    st.session_state.cam_enabled = True

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

# ── CSS Overrides (Fixing Visibility) ──────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        font-family: 'Inter', sans-serif !important;
    }}

    /* === CRITICAL VISIBILITY FIXES === */
    /* Forces labels, toggles, and radio text to be visible in Light Mode */
    .stMarkdown p, .stMarkdown span, label, .stSlider p, div[data-testid="stWidgetLabel"] p {{
        color: {TEXT} !important;
        font-weight: 500 !important;
    }}
    
    /* Fixes visibility for radio buttons and toggles */
    div[data-testid="stRadio"] label p {{
        color: {TEXT} !important;
    }}

    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 20px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}

    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        font-size: 0.7rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
    }}

    .stButton > button {{
        border-radius: 12px !important;
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
    }}
    
    .live-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {ACCENT}15;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid {ACCENT}33;
    }}

    [data-baseweb="tab-list"] {{ border-bottom: 1px solid {BORDER} !important; gap: 20px !important; }}
    [data-baseweb="tab"] {{ color: {TEXT_DIM} !important; }}
    [data-baseweb="tab"][aria-selected="true"] {{ color: {TEXT} !important; border-bottom-color: {ACCENT} !important; }}
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
    invalid_labels = ["No Specimen Detected", "Scanning...", "Awaiting Data"]
    if label not in invalid_labels:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

# ── Header ────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])
with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin:0;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{ACCENT}; font-size:0.75rem; font-weight:700; letter-spacing:1px; margin-top:-5px;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)

with h_col2:
    if st.button("☀️" if st.session_state.dark_mode else "🌙", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    
    # SYSTEM CONTROLS (Camera/Sync)
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        st.session_state.cam_enabled = st.toggle("Enable Camera Feed", value=st.session_state.cam_enabled)
    with ctrl_col2:
        sync_active = st.toggle("Auto-Sync (3s)", value=False)

    tabs = st.tabs(["Optical Input", "Manual/Batch Archive"])
    
    with tabs[0]:
        if st.session_state.cam_enabled:
            st.markdown(f"""<div class="live-badge"><span style="color:{ACCENT}; font-size:0.7rem; font-weight:700;">SYSTEM LIVE</span></div>""", unsafe_allow_html=True)
            cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
                if sync_active:
                    time.sleep(3)
                    st.rerun()
        else:
            st.info("Camera disabled. Toggle switch above to activate.")
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        upload_mode = st.radio("Upload Mode", ["Single Specimen", "Batch Upload"], horizontal=True)
        
        if upload_mode == "Single Specimen":
            up = st.file_uploader("Upload Image", type=["jpg","png"], key="single_up")
            if up:
                img = PIL.Image.open(up)
                st.image(img, use_container_width=True)
                if st.button("Analyze Specimen", use_container_width=True):
                    label, conf = classify(img)
                    st.session_state.insect_res = (label, conf)
                    add_to_inventory(label)
        else:
            ups = st.file_uploader("Upload Multiple Images", type=["jpg","png"], accept_multiple_files=True, key="batch_up")
            if ups and st.button("Start Batch Analysis", use_container_width=True):
                prog = st.progress(0)
                for i, up in enumerate(ups):
                    label, conf = classify(PIL.Image.open(up))
                    add_to_inventory(label)
                    st.session_state.insect_res = (label, conf)
                    prog.progress((i + 1) / len(ups))
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">System Configuration</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        is_custom = st.toggle("Custom Judge Email", value=False)
        target_email = st.text_input("Recipient", value="agiridhar41@gmail.com") if is_custom else "agiridhar41@gmail.com"
        
        st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.75rem; font-weight:700; margin-top:15px; text-transform:uppercase;'>Population Threshold</p>", unsafe_allow_html=True)
        current_threshold = st.slider("Threshold", 1, 50, 5, label_visibility="collapsed")
        
        if st.button("Clear Data", use_container_width=True):
            st.session_state.inventory = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Intelligence Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow" style="color:{TEXT_DIM}">Latest Detection</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:700;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
