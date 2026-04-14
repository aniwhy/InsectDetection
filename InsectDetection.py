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
    "Aphids": {"status": "Invasive", "color": "#FF4B4B", "desc": "Small sap-sucking pests."},
    "Armyworm": {"status": "Invasive", "color": "#FF4B4B", "desc": "Highly destructive crop larvae."},
    "Beetle": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native ecological species."},
    "Bollworm": {"status": "Invasive", "color": "#FF4B4B", "desc": "Cotton and corn pest."},
    "Grasshopper": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native herbivore."},
    "Mites": {"status": "Invasive", "color": "#FF4B4B", "desc": "Plant-damaging arachnids."},
    "Mosquito": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native nuisance insect."},
    "Sawfly": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Common native defoliator."},
    "Stem Borer": {"status": "Invasive", "color": "#FF4B4B", "desc": "Internal plant tissue feeder."}
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
    
    .main, [data-testid="stAppViewContainer"] {{ 
        background: {BG_GRADIENT} !important; 
        font-family: 'Inter', sans-serif !important; 
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Header Styling */
    .header-container {{ text-align: center; padding: 40px 0 20px 0; }}
    
    /* Clean Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 45px;
        background-color: {SURFACE};
        border-radius: 12px 12px 0 0;
        padding: 0 24px;
        border: 1px solid {BORDER};
        border-bottom: none;
        transition: all 0.3s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {ACCENT} !important;
        color: white !important;
    }}

    .bento-card {{ background: {CARD_BG}; backdrop-filter: blur(12px); border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    .stButton > button {{ border-radius: 14px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }}
    .stMarkdown p, label {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Header & Theme Toggle ─────────────────────────────────
t_col1, t_col2, t_col3 = st.columns([1, 8, 1])

with t_col2:
    st.markdown(f"""
        <div class="header-container">
            <h1 style="font-family:'Playfair Display'; color:{TEXT}; font-size: 4.5rem; margin:0; line-height:1;">Insect Detection</h1>
            <p style="color:{ACCENT}; font-size:0.85rem; font-weight:700; letter-spacing:4px; margin-top:10px; opacity:0.8;">
                TSA 2026 &nbsp; | &nbsp; ENGINEERING DESIGN &nbsp; | &nbsp; TEAM 2043-901
            </p>
        </div>
    """, unsafe_allow_html=True)

with t_col3:
    st.write(" ") # Padding
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('exp.pt') 

model = load_model()

def classify(img):
    results = model.predict(source=img, conf=0.25, verbose=False)
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
    info = INSECT_DATABASE.get(species, {"status": "Unknown"})
    msg = EmailMessage()
    msg.set_content(f"ALERT: {species} ({info['status']}) detected. Population: {count}")
    msg['Subject'] = f"⚠️ TSA ALERT: {species} Threshold Reached"
    msg['From'], msg['To'] = sender_email, recipient
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except: return False

# ── Main UI Content ───────────────────────────────────────
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown('<p class="eyebrow">Evaluation Inputs</p>', unsafe_allow_html=True)
    tabs = st.tabs(["LIVE FEED", "ARCHIVE UPLOAD"])
    
    with tabs[0]:
        # Live View Toggle
        st.session_state.cam_enabled = st.toggle("Enable Live Camera", value=st.session_state.cam_enabled)
        
        if st.session_state.cam_enabled:
            cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
            if cam_image:
                label, conf = classify(PIL.Image.open(cam_image))
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
        else:
            st.info("Live feed is currently disabled.")

    with tabs[1]:
        up = st.file_uploader("Select Image", type=["jpg","png"], label_visibility="collapsed")
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
    info = INSECT_DATABASE.get(label, {"status": "Unknown", "color": ACCENT, "desc": ""})
    
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
            <p style="color:{TEXT_DIM}; font-size:0.8rem; margin-top:10px;">{info['desc']}</p>
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

    st.markdown('<p class="eyebrow" style="margin-top:20px;">System Configs</p>', unsafe_allow_html=True)
    with st.expander("Configuration Settings"):
        target_email = st.text_input("Alert Destination", value="agiridhar41@gmail.com")
        threshold = st.slider("Population Alert Threshold", 1, 50, 5)
        if st.button("Reset Session Data", use_container_width=True):
            st.session_state.inventory = {}
            st.session_state.emails_sent = []
            st.rerun()

# ── Bottom Reference Section ────────────────────────────────
st.markdown("---")
st.markdown('<p class="eyebrow" style="text-align:center;">Species Classification Reference</p>', unsafe_allow_html=True)
ref_cols = st.columns(3)
items = list(INSECT_DATABASE.items())
for i, (name, data) in enumerate(items):
    with ref_cols[i % 3]:
        st.markdown(f"""
            <div style="padding:15px; border-radius:15px; border:1px solid {BORDER}; background:{SURFACE}; margin-bottom:10px;">
                <b style="color:{TEXT};">{name}</b><br>
                <span style="color:{data['color']}; font-size:0.7rem; font-weight:800;">{data['status'].upper()}</span><br>
                <span style="color:{TEXT_DIM}; font-size:0.75rem;">{data['desc']}</span>
            </div>
        """, unsafe_allow_html=True)

# ── Email Automation Trigger ────────────────────────────────
for species, count in st.session_state.inventory.items():
    if count >= threshold and species not in st.session_state.emails_sent:
        if INSECT_DATABASE.get(species, {}).get("status") == "Invasive":
            if send_email_alert(species, count, target_email):
                st.session_state.emails_sent.append(species)
                st.success(f"📧 Alert Sent for {species}!")
