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

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        font-family: 'Inter', sans-serif !important;
    }}

    /* === FIX FOR MISSING TOGGLE TEXT === */
    /* Targets the label specifically to force color visibility */
    div[data-testid="stWidgetLabel"] p {{
        color: {TEXT} !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }}
    
    .stMarkdown p, .stMarkdown span {{
        color: {TEXT};
    }}

    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}77; }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 6px {ACCENT}00; }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}00; }}
    }}

    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 20px; 
        padding: 24px; 
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
        font-family: 'Inter', sans-serif !important;
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
    .dot {{
        height: 8px; width: 8px;
        background-color: {ACCENT};
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}

    [data-baseweb="tab-list"] {{ border-bottom: 1px solid {BORDER} !important; gap: 20px !important; }}
    [data-baseweb="tab"] {{ color: {TEXT_DIM} !important; padding: 10px 0px !important; }}
    [data-baseweb="tab"][aria-selected="true"] {{ color: {TEXT} !important; border-bottom-color: {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic ──────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')

model = load_model()

def classify(img):
    return "Common Beetle", 0.94

def add_to_inventory(label, target_email, threshold):
    invalid_labels = ["No Specimen Detected", "Scanning...", "Awaiting Data"]
    if label not in invalid_labels:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1

# ── Header ────────────────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])

with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin:0;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{ACCENT}; font-size:0.75rem; font-weight:700; letter-spacing:1px; margin-top:-5px;">ENGINEERING DESIGN PORTFOLIO</p>', unsafe_allow_html=True)

with h_col2:
    # Uses the star/moon/sun logic based on your uploaded UI screenshots
    icon = "☀️" if st.session_state.dark_mode else "🌙"
    if st.button(icon, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    
    t1, t2 = st.columns(2)
    with t1:
        st.session_state.cam_enabled = st.toggle("Enable Camera Feed", value=st.session_state.cam_enabled)
    with t2:
        sync_active = st.toggle("Auto-Sync (3s)", value=False)

    tabs = st.tabs(["Optical Input", "Manual Archive"])
    
    with tabs[0]:
        if st.session_state.cam_enabled:
            st.markdown(f"""<div class="live-badge"><div class="dot"></div><span style="color:{ACCENT}; font-size:0.7rem; font-weight:700;">SYSTEM LIVE</span></div>""", unsafe_allow_html=True)
            st.write("")
            
            cam_placeholder = st.empty()
            cam_image = cam_placeholder.camera_input("Snapshot", label_visibility="collapsed")
            
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, "agiridhar41@gmail.com", 5)
                
                if sync_active:
                    time.sleep(3)
                    st.rerun()
        else:
            st.info("Camera input is currently disabled via system toggle.")
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Upload Image", type=["jpg","png"])
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Process Image", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, "agiridhar41@gmail.com", 5)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">System Configuration</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        st.text_input("Recipient Email", value="agiridhar41@gmail.com")
        st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.75rem; font-weight:700; margin-top:15px; text-transform:uppercase;'>Alert Threshold</p>", unsafe_allow_html=True)
        current_threshold = st.slider("Threshold", 1, 50, 5, label_visibility="collapsed")
        
        # Clear button with the blue sync icon as per your screenshot
        if st.button("🔄 Clear Data", use_container_width=True):
            st.session_state.inventory = {}
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Intelligence Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow" style="color:{TEXT_DIM}">Latest Identification</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:700;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="bento-card"><p class="eyebrow">Population Tracker</p>', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.9rem;'>No records logged.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid {BORDER}55;">
                    <span style="color:{TEXT}; font-weight:500;">{species}</span>
                    <span style="color:{ACCENT}; font-weight:700;">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; border-top:1px solid {BORDER}; padding-top:24px;">
        <p style="color:{ACCENT}; font-weight:800; letter-spacing:2px; font-size:0.75rem; margin:0;">ENGINEERING DESIGN</p>
        <p style="color:{TEXT_DIM}; font-size:0.7rem; font-weight:500; margin-top:5px;">TEAM ID: 2043-901 | SEVEN SPRINGS, PA</p>
    </div>
""", unsafe_allow_html=True)
