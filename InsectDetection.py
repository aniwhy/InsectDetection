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

# ── Initialize Session State ──────────────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "reset_confirmed" not in st.session_state:
    st.session_state.reset_confirmed = False

# ── Color Palettes ────────────────────────────────────────
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

# Apply current theme colors
colors = DARK_PALETTE if st.session_state.dark_mode else LIGHT_PALETTE
BG, CARD, TEXT, TEXT_DIM, ACCENT, BORDER = (
    colors["BG"], colors["CARD"], colors["TEXT"], colors["TEXT_DIM"], colors["ACCENT"], colors["BORDER"]
)

# ── CSS Overrides ─────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-color: {BG} !important; }}
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        color: {TEXT} !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Global Text Color Fix for Streamlit widgets */
    .stMarkdown p, .stText, label, [data-testid="stWidgetLabel"] p {{
        color: {TEXT} !important;
    }}

    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px;
    }}
    
    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 2px; font-size: 0.7rem; font-weight: 700; 
        color: {ACCENT} !important; margin-bottom: 8px;
    }}
    
    /* Toggle Switch */
    div[role="switch"] {{ background-color: {EARTH_BROWN} !important; border: 1px solid {BORDER} !important; }}
    div[role="switch"][aria-checked="true"] {{ background-color: {ACCENT} !important; }}
    
    /* Slider (No Red) */
    div[data-baseweb="slider"] [role="slider"] {{
        background-color: {ACCENT} !important;
        border: 2px solid {TEXT} !important;
    }}
    div[data-baseweb="slider"] > div > div {{ background: {BORDER} !important; }}
    div[data-baseweb="slider"] div[data-testid="stTickBar"] + div > div > div:first-child {{
        background-color: {ACCENT} !important;
    }}

    /* Tabs */
    [data-baseweb="tab-list"] {{ border-bottom: 2px solid {BORDER} !important; }}
    [data-baseweb="tab"] {{ color: {TEXT_DIM} !important; }}
    [data-baseweb="tab"][aria-selected="true"] {{ 
        color: {TEXT} !important; 
        border-bottom: 3px solid {ACCENT} !important; 
    }}
</style>
""", unsafe_allow_html=True)

# ── Email Function ────────────────────────────────────────
def send_pest_control_email(species, count, receiver_email, threshold):
    sender = "aniyuva745@gmail.com"
    password = "crei kema pjwg djwl" # App Password
    
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver_email
    msg["Subject"] = f"TSA ALERT: Population Influx ({species.title()})"
    
    body = f"Threshold reached for {species}. Count: {count}. Threshold: {threshold}."
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# ── YOLO Logic ───────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('exp-2.pt')

model = load_model()

def classify(img):
    results = model.predict(img, verbose=False)
    if results and results[0].probs:
        conf = results[0].probs.top1conf.item()
        label = model.names[results[0].probs.top1]
        if conf < 0.55: return "No Specimen Detected", conf
        return label, conf
    return "Scanning...", 0.0

# ── Header & Theme Toggle ─────────────────────────────────
t_col1, t_col2 = st.columns([8, 2])
with t_col1:
    st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT};">Insect Detection</h1>', unsafe_allow_html=True)
with t_col2:
    # Logic to handle state change and trigger rerun for color swap
    current_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    if current_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = current_mode
        st.rerun()

# ── Main Layout ───────────────────────────────────────────
col_left, col_right = st.columns([1.5, 1])

with col_right:
    st.markdown('<p class="eyebrow">Agency Configuration</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    target_email = st.text_input("Recipient Email", value="agiridhar41@gmail.com")
    st.markdown(f"<p style='color: {TEXT_DIM}; font-size:0.75rem; font-weight:700;'>ALERT THRESHOLD</p>", unsafe_allow_html=True)
    current_threshold = st.slider("Threshold", 1, 50, 5, label_visibility="collapsed")
    
    if st.button("🔄 Clear Data", use_container_width=True):
        st.session_state.inventory = {}
        st.session_state.emails_sent = []
        st.toast("Inventory Reset")
    st.markdown('</div>', unsafe_allow_html=True)

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    tabs = st.tabs(["Camera Control", "Manual Upload"])
    
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            img = PIL.Image.open(cam_image)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)
            
            # Logic for inventory
            if label not in ["No Specimen Detected", "Scanning..."]:
                st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
                if st.session_state.inventory[label] >= current_threshold and label not in st.session_state.emails_sent:
                    if send_pest_control_email(label, st.session_state.inventory[label], target_email, current_threshold):
                        st.session_state.emails_sent.append(label)
                        st.toast(f"Email Alert Sent to {target_email}!", icon="✅")

    with tabs[1]:
        up = st.file_uploader("Upload Image", type=["jpg","png"])
        if up and st.button("Process Image"):
            img = PIL.Image.open(up)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)

with col_right:
    st.markdown('<p class="eyebrow">Identification</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card">
            <div style="font-family:'Playfair Display'; font-size: 2rem; color:{TEXT};">{label.replace('_',' ').title()}</div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; font-weight: 600;">Confidence: {conf:.2%}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Population Inventory</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM};'>No specimens logged.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            over = count >= current_threshold
            c = ACCENT if over else TEXT
            st.markdown(f'<div style="display:flex; justify-content:space-between; color:{c};"><span>{species.title()}</span><b>{count}</b></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f'<p style="text-align:center; color:{TEXT_DIM}; font-size:0.7rem; margin-top:2rem;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)
