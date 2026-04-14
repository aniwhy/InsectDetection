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
    initial_sidebar_state="collapsed"
)

# ── THE MASTER DICTIONARY ─────────────────────────────────
# These MUST match the folder names/labels in your dataset.
INSECT_DATABASE = {
    "bollworm": {"status": "Invasive", "color": "#FF4B4B", "desc": "High-risk agricultural pest"},
    "armyworm": {"status": "Invasive", "color": "#FF4B4B", "desc": "Highly destructive to foliage"},
    "stem_borer": {"status": "Invasive", "color": "#FF4B4B", "desc": "Internal plant tissue feeder"},
    "aphids": {"status": "Invasive", "color": "#FF4B4B", "desc": "Sap-sucker & virus vector"},
    "mites": {"status": "Invasive", "color": "#FF4B4B", "desc": "High infestation potential"},
    "mosquito": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native ecological nuisance"},
    "sawfly": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Common native defoliator"},
    "beetle": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "General native species"},
    "grasshopper": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native herbivore"}
}

# ── Initialize Session State ───────────────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "cam_enabled" not in st.session_state:
    st.session_state.cam_enabled = True
if "insect_res" not in st.session_state:
    st.session_state.insect_res = ("Awaiting Data", 0.0)

# ── Theme Colors ───────────────────────────────────────────
if st.session_state.dark_mode:
    BG_GRADIENT, CARD_BG, TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)", "rgba(20, 30, 20, 0.7)", "#E0E4E0", "#8AA38D", "#4CAF50", "#2D362E", "#1A1D1A"
else:
    BG_GRADIENT, CARD_BG, TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "linear-gradient(135deg, #F0F7F0 0%, #E2E8E2 100%)", "rgba(255, 255, 255, 0.6)", "#1B2E1B", "#4A5D4C", "#2E8B57", "#C2D9C5", "#F0F2F0"

# ── CSS ────────────────────────────────────────────────────
st.markdown(f"<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap'); [data-testid='stHeader'], header, footer {{ visibility: hidden; display: none; }} .main, [data-testid='stAppViewContainer'] {{ background: {BG_GRADIENT} !important; font-family: 'Inter', sans-serif !important; }} .bento-card {{ background: {CARD_BG}; backdrop-filter: blur(12px); border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; }} .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }} .stButton > button {{ border-radius: 14px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }} .stMarkdown p, label {{ color: {TEXT} !important; }}</style>", unsafe_allow_html=True)

# ── Logic ──────────────────────────────────────────────────
@st.cache_resource
def load_model():
    # MAKE SURE THIS FILE EXISTS IN YOUR FOLDER
    return YOLO('yolov8n.pt') 

model = load_model()

def classify(img):
    results = model(img)
    # This checks if the model actually predicted classes
    if hasattr(results[0], 'probs') and results[0].probs is not None:
        idx = int(results[0].probs.top1)
        label = results[0].names[idx]
        conf = float(results[0].probs.top1conf)
        print(f"DEBUG: Model detected '{label}' with {conf} confidence") # Check your terminal for this!
        return label, conf
    return "No Specimen Detected", 0.0

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label.replace('_', ' ').title()}", icon="🐞")

# ── UI Layout ──────────────────────────────────────────────
st.markdown(f"<div style='text-align:center; padding:40px 0;'><h1 style='font-family:\"Playfair Display\"; color:{TEXT}; font-size: 4rem; margin:0;'>Insect Detection</h1><p style='color:{ACCENT}; font-weight:700; letter-spacing:3px;'>TSA 2026 | TEAM 2043-901</p></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.session_state.cam_enabled = st.toggle("Enable Live Camera", value=st.session_state.cam_enabled)
    t1, t2 = st.tabs(["LIVE FEED", "UPLOAD"])
    
    with t1:
        if st.session_state.cam_enabled:
            cam_img = st.camera_input("Capture", label_visibility="collapsed")
            if cam_img:
                label, conf = classify(PIL.Image.open(cam_img))
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

    with t2:
        up = st.file_uploader("Upload Image", type=["jpg","png"])
        if up and st.button("Analyze Upload"):
            label, conf = classify(PIL.Image.open(up))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)

with col_right:
    label, conf = st.session_state.insect_res
    clean_label = label.lower().replace(" ", "_")
    info = INSECT_DATABASE.get(clean_label, {"status": "Unknown", "color": "#888888", "desc": "Check model labels"})

    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {info['color']};">
            <div style="display:flex; justify-content:space-between;">
                <p class="eyebrow">Result</p>
                <span style="background:{info['color']}22; color:{info['color']}; padding:2px 8px; border-radius:5px; font-size:0.7rem; font-weight:800;">{info['status']}</span>
            </div>
            <h2 style="font-family:'Playfair Display'; font-size: 2.5rem; color:{TEXT}; margin:0;">{label.replace('_', ' ').title()}</h2>
            <p style="color:{TEXT_DIM}; font-size:0.8rem;">{info['desc']}</p>
            <hr style="border:0; border-top:1px solid {BORDER}; margin:15px 0;">
            <div style="display:flex; justify-content:space-between;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:800;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Session Inventory</p>', unsafe_allow_html=True)
    for insect, count in st.session_state.inventory.items():
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid {BORDER};'><span style='color:{TEXT};'>{insect.title()}</span><span style='color:{ACCENT}; font-weight:700;'>{count}</span></div>", unsafe_allow_html=True)

    if st.button("Clear Data", use_container_width=True):
        st.session_state.inventory = {}; st.rerun()
