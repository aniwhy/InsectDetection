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

# ── Invasive Status Database ──────────────────────────────
INSECT_DATABASE = {
    "Aphids": {"status": "Invasive", "color": "#FF4B4B"},
    "Armyworm": {"status": "Invasive", "color": "#FF4B4B"},
    "Beetle": {"status": "Non-Invasive", "color": "#4CAF50"},
    "Bollworm": {"status": "Invasive", "color": "#FF4B4B"},
    "Grasshopper": {"status": "Non-Invasive", "color": "#4CAF50"},
    "Mites": {"status": "Invasive", "color": "#FF4B4B"},
    "Mosquito": {"status": "Non-Invasive", "color": "#4CAF50"},
    "Sawfly": {"status": "Non-Invasive", "color": "#4CAF50"},
    "Stem Borer": {"status": "Invasive", "color": "#FF4B4B"}
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

# ── Color Palettes ────────────────────────────────────────
if st.session_state.dark_mode:
    BG_GRADIENT = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)"
    CARD_BG = "rgba(20, 30, 20, 0.7)" 
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#E0E4E0", "#8AA38D", "#4CAF50", "#2D362E", "#1A1D1A"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F0F7F0 0%, #E2E8E2 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.6)"
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#1B2E1B", "#4A5D4C", "#2E8B57", "#C2D9C5", "#F0F2F0"

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ background: {BG_GRADIENT} !important; font-family: 'Inter', sans-serif !important; }}
    .bento-card {{ background: {CARD_BG}; backdrop-filter: blur(12px); border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; transition: all 0.3s ease; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    .stButton > button {{ border-radius: 14px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }}
    .stMarkdown p, label {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('exp.pt') 

model = load_model()

def classify(img):
    """Actual AI Inference Logic for Classification Models"""
    results = model.predict(source=img, conf=0.25, verbose=False)
    
    # exp.pt is a classification model, so we use .probs instead of .boxes
    if results[0].probs is not None:
        class_id = int(results[0].probs.top1)
        label = model.names[class_id].replace("_", " ").title()
        conf = float(results[0].probs.top1conf)
        return label, conf
    
    return "No Specimen Detected", 0.0

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

def send_email_alert(species, count, recipient):
    sender_email = "aniyuva745@gmail.com"
    sender_password = "xkoz kvqr xtjr atio"
    
    status_info = INSECT_DATABASE.get(species, {"status": "Unknown"})
    
    msg = EmailMessage()
    msg.set_content(f"INVASIVE SPECIES ALERT\n\nSpecies: {species}\nStatus: {status_info['status']}\nCount: {count}\n\nImmediate action may be required.")
    msg['Subject'] = f"⚠️ TSA ALERT: {species} ({status_info['status']})"
    msg['From'], msg['To'] = sender_email, recipient
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except: return False

# ── UI Layout ─────────────────────────────────────────────
st.markdown(f'<div style="text-align:center; padding:20px;"><h1 style="font-family:Playfair Display; color:{TEXT}; font-size:3.5rem;">Insect Detection</h1></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Evaluation Inputs</p>', unsafe_allow_html=True)
    tabs = st.tabs(["[ LIVE FEED ]", "[ ARCHIVE UPLOAD ]"])
    
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            label, conf = classify(PIL.Image.open(cam_image))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)

    with tabs[1]:
        up = st.file_uploader("Select Image", type=["jpg","png"])
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Run Classification", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

with col_right:
    st.markdown('<p class="eyebrow">Detection Metrics</p>', unsafe_allow_html=True)
    label, conf = st.session_state.insect_res
    
    # Get invasive data for UI
    info = INSECT_DATABASE.get(label, {"status": "Unknown", "color": ACCENT})
    
    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {info['color']};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <p class="eyebrow" style="color:{TEXT_DIM}">Identified Insect</p>
                    <div style="font-family:'Playfair Display'; font-size: 2.5rem; color:{TEXT}; line-height:1.1;">{label}</div>
                </div>
                <div style="background:{info['color']}22; color:{info['color']}; padding:4px 10px; border-radius:8px; font-size:0.7rem; font-weight:800; border:1px solid {info['color']};">
                    {info['status'].upper()}
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:20px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.85rem; font-weight:600;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:800; font-size:1.2rem;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Inventory</p>', unsafe_allow_html=True)
    with st.container(border=True):
        if not st.session_state.inventory:
            st.write("No specimens logged.")
        for species, count in st.session_state.inventory.items():
            s_info = INSECT_DATABASE.get(species, {"color": TEXT})
            st.markdown(f"<p style='margin:0;'><b>{species}</b>: <span style='color:{s_info['color']};'>{count}</span></p>", unsafe_allow_html=True)

    # Email Logic
    threshold = st.sidebar.slider("Alert Threshold", 1, 20, 5)
    target_email = st.sidebar.text_input("Alert Email", "agiridhar41@gmail.com")
    
    for species, count in st.session_state.inventory.items():
        if count >= threshold and species not in st.session_state.emails_sent:
            # Only trigger email if species is INVASIVE
            if INSECT_DATABASE.get(species, {}).get("status") == "Invasive":
                if send_email_alert(species, count, target_email):
                    st.session_state.emails_sent.append(species)
                    st.sidebar.success(f"Email sent for {species}!")
