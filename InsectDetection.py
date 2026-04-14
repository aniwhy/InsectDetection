import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time
import smtplib
from email.message import EmailMessage

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Detection | TSA 2026",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Initialize Session State ───────────────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "insect_res" not in st.session_state:
    st.session_state.insect_res = ("Awaiting Data", 0.0)

# ── Sidebar Theme Toggle ──────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")
    if st.button("🌓 Switch Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Color Palettes ────────────────────────────────────────
if st.session_state.dark_mode:
    BG_GRADIENT = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)"
    CARD_BG = "rgba(20, 30, 20, 0.7)" 
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#E0E4E0", "#8AA38D", "#4CAF50", "#2D362E", "#1A1D1A"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F6FAF6 0%, #DDE4DD 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.8)"
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#1B2E1B", "#4A5D4C", "#2E8B57", "#C2D9C5", "#FFFFFF"

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    
    /* Global Transition for Theme Switching */
    .main, [data-testid="stAppViewContainer"], .bento-card, .stMarkdown, p, div {{
        transition: background-color 0.6s ease, background 0.6s ease, color 0.6s ease, border-color 0.6s ease !important;
    }}

    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    
    .main, [data-testid="stAppViewContainer"] {{ 
        background: {BG_GRADIENT} !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    /* Bento Box Styling */
    .bento-card {{ 
        background: {CARD_BG}; 
        backdrop-filter: blur(12px); 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px; 
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.05);
    }}

    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-size: 0.75rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px; 
    }}

    /* Improved Tab Label Styling */
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
        border: 1px solid {BORDER} !important;
        border-radius: 50px !important;
        padding: 8px 20px !important;
        margin: 0 5px !important;
        transition: all 0.3s ease !important;
    }}
    
    button[data-baseweb="tab"] p {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
    }}

    button[aria-selected="true"] {{
        background-color: {ACCENT} !important;
        border-color: {ACCENT} !important;
    }}
    
    button[aria-selected="true"] p {{
        color: white !important;
    }}

    .stButton > button {{ 
        border-radius: 14px !important; 
        background-color: {SURFACE} !important; 
        color: {TEXT} !important; 
        border: 1px solid {BORDER} !important; 
        width: 100%;
    }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    # Use 'yolov8n.pt' or your custom 'exp.pt'
    return YOLO('yolov8n.pt') 

model = load_model()

def classify(img):
    results = model.predict(source=img, conf=0.25, verbose=False)
    if len(results[0].boxes) > 0:
        top_box = results[0].boxes[0]
        class_id = int(top_box.cls[0])
        label = model.names[class_id].replace("_", " ").title()
        conf = float(top_box.conf[0])
        return label, conf
    return "No Specimen Detected", 0.0

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

# ── UI Layout ─────────────────────────────────────────────
st.markdown(f'<div style="text-align:center; padding:20px;"><h1 style="font-family:Playfair Display; color:{TEXT}; font-size:3.5rem; margin-bottom:0;">Insect Detection</h1><p style="color:{TEXT_DIM}; opacity:0.7;">TSA 2026 RESEARCH PORTAL</p></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown('<p class="eyebrow">Evaluation Inputs</p>', unsafe_allow_html=True)
    tabs = st.tabs(["LIVE FEED", "ARCHIVE UPLOAD"])
    
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            label, conf = classify(PIL.Image.open(cam_image))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)

    with tabs[1]:
        up = st.file_uploader("Select Image", type=["jpg","png"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Analyze Specimen"):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

with col_right:
    st.markdown('<p class="eyebrow">Detection Metrics</p>', unsafe_allow_html=True)
    label, conf = st.session_state.insect_res
    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {ACCENT};">
            <p class="eyebrow" style="color:{TEXT_DIM}">Identified Insect</p>
            <div style="font-family:'Playfair Display'; font-size: 2.5rem; color:{TEXT};">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:15px; border-top: 1px solid {BORDER}; padding-top:10px;">
                <span style="color:{TEXT_DIM};">Confidence</span>
                <span style="color:{ACCENT}; font-weight:800;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Inventory</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        if not st.session_state.inventory:
            st.markdown(f'<p style="color:{TEXT_DIM};">No specimens logged.</p>', unsafe_allow_html=True)
        for species, count in st.session_state.inventory.items():
            st.markdown(f"**{species}**: {count}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Email Logic & Threshold (Simplified for demo)
    threshold = st.sidebar.slider("Alert Threshold", 1, 20, 5)
    target_email = st.sidebar.text_input("Alert Email", "user@example.com")
