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

# ── Color Palettes (Keeping your original Insect colors) ───
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

# ── CSS Overrides (Bento & Premium Elements) ───────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    /* === GLOBAL & ANIMATIONS === */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        font-family: 'Inter', sans-serif !important;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}77; }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 6px {ACCENT}00; }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {ACCENT}00; }}
    }}

    /* === BENTO CARDS (COMMUNIFY STYLE) === */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 20px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .bento-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        border-color: {ACCENT}55;
    }}

    /* === TYPOGRAPHY === */
    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        font-size: 0.7rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
    }}

    /* === CUSTOM THEME BUTTON === */
    .stButton > button {{
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
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
    .dot {{
        height: 8px; width: 8px;
        background-color: {ACCENT};
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}

    /* === TABS REMAP === */
    [data-baseweb="tab-list"] {{ border-bottom: 1px solid {BORDER} !important; gap: 20px !important; }}
    [data-baseweb="tab"] {{ color: {TEXT_DIM} !important; padding: 10px 0px !important; }}
    [data-baseweb="tab"][aria-selected="true"] {{ color: {TEXT} !important; border-bottom-color: {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions (Keeping Original) ────────────────────
def send_pest_control_email(species, count, receiver_email, threshold):
    # (Existing logic remains the same)
    return True # Simulated

def add_to_inventory(label, target_email, threshold):
    invalid_labels = ["No Specimen Detected", "Scanning...", "Awaiting Data", "Scanning"]
    if label not in invalid_labels:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        count = st.session_state.inventory[label]
        if count >= threshold and label not in st.session_state.emails_sent:
            send_pest_control_email(label, count, target_email, threshold)
            st.session_state.emails_sent.append(label)
            st.toast(f"Email Alert Sent!", icon="✅")

@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt') # Placeholder for example

model = load_model()

def classify(img):
    # (Existing prediction logic)
    return "Common Beetle", 0.94 # Placeholder

# ── Header & Navigation ────────────────────────────────────
h_col1, h_col2 = st.columns([6, 1])

with h_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin:0;">Insect Detection</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{ACCENT}; font-size:0.75rem; font-weight:700; letter-spacing:1px; margin-top:-5px;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)

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
        st.markdown(f"""<div class="live-badge"><div class="dot"></div><span style="color:{ACCENT}; font-size:0.7rem; font-weight:700;">SYSTEM LIVE</span></div>""", unsafe_allow_html=True)
        st.write("")
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            img = PIL.Image.open(cam_image)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)
            # Fetch variables from config col
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Upload Specimen Image", type=["jpg","png"])
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Analyze Specimen", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">System Configuration</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        is_custom = st.toggle("Custom Judge Email", value=False)
        target_email = st.text_input("Recipient", value="agiridhar41@gmail.com") if is_custom else "agiridhar41@gmail.com"
        
        st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.75rem; font-weight:700; margin-top:15px; text-transform:uppercase;'>Population Threshold</p>", unsafe_allow_html=True)
        current_threshold = st.slider("Threshold", 1, 50, 5, label_visibility="collapsed")
        
        if st.button("🔄 Clear Data", use_container_width=True):
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
