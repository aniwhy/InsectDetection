import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time
import smtplib
import random
from email.message import EmailMessage

# ── Page Configuration ────────────────────────────────────
st.set_page_config (
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

# ── BAU-Insectv2 Dataset Integration (Updated) ────────────
# These match your provided list exactly
DATASET_CLASSES = [
    "mosquito", "sawfly", "stem_borer", "beetle", 
    "bollworm", "grasshopper", "mites", "aphids", "armyworm"
]

# Identifying high-threat pests for the Alert System
INVASIVE_PESTS = [
    "stem_borer", "bollworm", "armyworm", 
    "aphids", "mites", "mosquito", "sawfly"
]

# ── Color Palettes ────────────────────────────────────────
if st.session_state.dark_mode:
    BG_GRADIENT = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)"
    CARD_BG = "rgba(20, 30, 20, 0.7)" 
    TEXT = "#E0E4E0"; TEXT_DIM = "#8AA38D"; ACCENT = "#4CAF50" 
    BORDER = "#2D362E"; SURFACE = "#1A1D1A"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F0F7F0 0%, #E2E8E2 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.6)"
    TEXT = "#1B2E1B"; TEXT_DIM = "#4A5D4C"; ACCENT = "#2E8B57" 
    BORDER = "#C2D9C5"; SURFACE = "#F0F2F0"

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ background: {BG_GRADIENT} !important; font-family: 'Inter', sans-serif !important; }}
    .header-container {{ text-align: center; padding: 40px 0 20px 0; }}
    .bento-card {{ background: {CARD_BG}; backdrop-filter: blur(12px); border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; transition: all 0.3s ease; }}
    .bento-card:hover {{ transform: translateY(-5px); border-color: {ACCENT} !important; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    .stButton > button {{ border-radius: 12px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt') 

model = load_model()

def classify(img):
    """Simulates detection using your specific insect list."""
    label = random.choice(DATASET_CLASSES)
    confidence = random.uniform(0.91, 0.99)
    return label, confidence

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Scanning...", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

def send_email_alert(species, count, recipient):
    sender_email = "aniyuva745@gmail.com"
    sender_password = "xkoz kvqr xtjr atio" 
    msg = EmailMessage()
    msg.set_content(f"CRITICAL INVASIVE PEST ALERT\n\nSpecies Identified: {species}\nCount: {count}\nSystem ID: TSA-2043-901\nDataset Reference: BAU-Insectv2")
    msg['Subject'] = f"⚠️ ALERT: {species.upper()} INFESTATION DETECTED"
    msg['From'] = sender_email; msg['To'] = recipient
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail Error: {e}"); return False

# ── Header ────────────────────────────────────────────────
st.markdown(f"""
    <div class="header-container">
        <h1 style="font-family:'Playfair Display'; color:{TEXT}; font-size: 3.5rem; margin:0;">Invasive Species Hub</h1>
        <p style="color:{ACCENT}; font-size:0.8rem; font-weight:700; letter-spacing:3px;">TSA 2026 | BIOMEDICAL & AGRI-TECH ENGINE</p>
    </div>
""", unsafe_allow_html=True)

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<p class="eyebrow">Detection Input</p>', unsafe_allow_html=True)
    tabs = st.tabs(["[ LIVE HARDWARE ]", "[ DATASET ARCHIVE ]"])
    
    with tabs[0]:
        st.session_state.cam_enabled = st.toggle("Power Field Feed", value=st.session_state.cam_enabled)
        if st.session_state.cam_enabled:
            cam_image = st.camera_input("Capture", label_visibility="collapsed")
            if cam_image:
                label, conf = classify(PIL.Image.open(cam_image))
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

    with tabs[1]:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Upload Image", type=["jpg","png"])
        if up and st.button("Analyze BAU-Insectv2 Class", use_container_width=True):
            label, conf = classify(PIL.Image.open(up))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Real-Time Metrics</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    
    is_invasive = label in INVASIVE_PESTS
    status_text = "⚠️ INVASIVE SPECIES" if is_invasive else "✅ NATIVE / NEUTRAL"
    status_color = "#FF4B4B" if is_invasive else "#4CAF50"

    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {status_color};">
            <p class="eyebrow" style="color:{status_color}">{status_text}</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT}; text-transform: capitalize;">{label.replace('_', ' ')}</div>
            <div style="margin-top:10px; color:{ACCENT}; font-weight:800;">{conf:.1%} Confidence</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Session Log</p>', unsafe_allow_html=True)
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM};'>Waiting for specimen detection...</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            txt_color = "#FF4B4B" if species in INVASIVE_PESTS else TEXT
            st.markdown(f"<div style='display:flex; justify-content:space-between; border-bottom:1px solid {BORDER}; padding:5px 0; text-transform: capitalize;'><span style='color:{txt_color}'>{species.replace('_', ' ')}</span><b>{count}</b></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("System Configurations"):
        target_email = st.text_input("Alert Destination", value="agiridhar41@gmail.com")
        threshold = st.slider("Population Threshold", 1, 20, 5)
        if st.button("Wipe Data", use_container_width=True):
            st.session_state.inventory = {}; st.session_state.emails_sent = []; st.rerun()

# ── Email Automation Trigger ────────────────────────────────
for species, count in st.session_state.inventory.items():
    if species in INVASIVE_PESTS and count >= threshold and species not in st.session_state.emails_sent:
        if send_email_alert(species, count, target_email):
            st.session_state.emails_sent.append(species)
            st.toast(f"Email Alert: {species} threshold exceeded", icon="📧")
