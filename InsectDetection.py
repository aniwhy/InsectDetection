import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time
import smtplib
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

# ── Color Palettes (Rich Green Enhancements) ──────────────
if st.session_state.dark_mode:
    BG_GRADIENT = "linear-gradient(135deg, #0A0F0A 0%, #121412 100%)"
    CARD_BG = "rgba(20, 30, 20, 0.7)" 
    TEXT = "#E0E4E0"
    TEXT_DIM = "#8AA38D"
    ACCENT = "#4CAF50" 
    BORDER = "#2D362E"
    SURFACE = "#1A1D1A"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F0F7F0 0%, #E2E8E2 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.6)"
    TEXT = "#1B2E1B"
    TEXT_DIM = "#4A5D4C"
    ACCENT = "#2E8B57" 
    BORDER = "#C2D9C5"
    SURFACE = "#F0F2F0"

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
    
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    
    .main, [data-testid="stAppViewContainer"] {{ 
        background: {BG_GRADIENT} !important; 
        font-family: 'Inter', sans-serif !important;
        transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .header-container {{
        text-align: center;
        padding: 40px 0 20px 0;
    }}

    .bento-card {{ 
        background: {CARD_BG}; 
        backdrop-filter: blur(12px);
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 50, 0, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}
    
    .bento-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 45px rgba(76, 175, 80, 0.15);
        border-color: {ACCENT} !important;
    }}

    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-size: 0.75rem; 
        font-weight: 800; 
        color: {ACCENT}; 
        margin-bottom: 12px;
    }}

    .stButton > button {{
        border-radius: 14px !important;
        background-color: {SURFACE} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        font-weight: 600 !important;
    }}

    .stButton > button:hover {{
        background-color: {ACCENT}22 !important;
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
    }}

    .stMarkdown p, .stMarkdown span, label, .stSlider p, div[data-testid="stWidgetLabel"] p, div[data-testid="stRadio"] label p {{
        color: {TEXT} !important;
    }}

    .live-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {ACCENT}22;
        padding: 6px 14px;
        border-radius: 30px;
        border: 1px solid {ACCENT}44;
    }}

    [data-baseweb="tab-list"] {{ border-bottom: 1px solid {BORDER} !important; }}
    [data-baseweb="tab"] {{ color: {TEXT_DIM} !important; font-weight: 600; }}
    [data-baseweb="tab"][aria-selected="true"] {{ color: {ACCENT} !important; border-bottom-color: {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt') 

model = load_model()

def classify(img):
    # Simulated prediction for UI testing
    return "Common Beetle", 0.94 

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Scanning...", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label}", icon="🐞")

def send_email_alert(species, count, recipient):
    """Sends an automated email alert using provided credentials."""
    sender_email = "aniyuva745@gmail.com"
    sender_password = "xkoz kvqr xtjr atio"
    
    msg = EmailMessage()
    msg.set_content(f"""
    INVASIVE SPECIES ALERT
    ----------------------
    System ID: TSA-2026-HQ
    Species Identified: {species}
    Current Population Count: {count}
    Status: Threshold Exceeded
    """)
    
    msg['Subject'] = f"⚠️ ALERT!!: {species} Threshold Reached"
    msg['From'] = sender_email
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Mail System Error: {e}")
        return False

# ── Header Section ────────────────────────────────────────
st.markdown(f"""
    <div class="header-container">
        <h1 style="font-family:'Playfair Display'; color:{TEXT}; font-size: 4rem; margin:0;">Insect Detection</h1>
        <p style="color:{ACCENT}; font-size:0.9rem; font-weight:700; letter-spacing:3px; margin-top:5px;">
            TSA 2026 &nbsp; | &nbsp; ENGINEERING DESIGN &nbsp; | &nbsp; TEAM 2043-901
        </p>
    </div>
""", unsafe_allow_html=True)

t_col1, t_col2, t_col3 = st.columns([1, 8, 1])
with t_col3:
    if st.button("☀️" if st.session_state.dark_mode else "🌙", help="Switch Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.markdown("---", unsafe_allow_html=True)

# ── Main Layout ────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown('<p class="eyebrow">Evaluation Inputs</p>', unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        st.session_state.cam_enabled = st.toggle("Enable Live Camera Feed", value=st.session_state.cam_enabled)
    with ctrl_col2:
        sync_active = st.toggle("Auto-Refresh Inventory", value=False)

    tabs = st.tabs(["[ LIVE FEED ]", "[ ARCHIVE UPLOAD ]"])
    
    with tabs[0]:
        if st.session_state.cam_enabled:
            st.markdown(f"""<div class="live-badge"><span style="color:{ACCENT}; font-size:0.75rem; font-weight:800;">● SYSTEM ACTIVE</span></div>""", unsafe_allow_html=True)
            cam_image = st.camera_input("Image", label_visibility="collapsed")
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
                if sync_active:
                    time.sleep(2)
                    st.rerun()
        else:
            st.info("Live feed is currently disabled. Toggle hardware feed above.")
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        upload_mode = st.radio("Processing Module", ["Single Insect", "Batch Processing"], horizontal=True)
        
        if upload_mode == "Single Insect":
            up = st.file_uploader("Select Image", type=["jpg","png"], key="single_up")
            if up:
                img = PIL.Image.open(up)
                st.image(img, use_container_width=True)
                if st.button("Run Classification", use_container_width=True):
                    label, conf = classify(img)
                    st.session_state.insect_res = (label, conf)
                    add_to_inventory(label)
        else:
            ups = st.file_uploader("Select Multiple Files", type=["jpg","png"], accept_multiple_files=True, key="batch_up")
            if ups and st.button("Execute Batch Analysis", use_container_width=True):
                prog = st.progress(0)
                for i, up in enumerate(ups):
                    label, conf = classify(PIL.Image.open(up))
                    add_to_inventory(label)
                    st.session_state.insect_res = (label, conf)
                    prog.progress((i + 1) / len(ups))
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Detection Metrics</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {ACCENT};">
            <p class="eyebrow" style="color:{TEXT_DIM}">Identified Insect</p>
            <div style="font-family:'Playfair Display'; font-size: 2.8rem; color:{TEXT}; line-height:1.1;">{label}</div>
            <div style="display:flex; justify-content:space-between; margin-top:20px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.85rem; font-weight:600;">Confidence Rating</span>
                <span style="color:{ACCENT}; font-weight:800; font-size:1.2rem;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Inventory</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM}; font-style:italic;'>No specimens logged in current session.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid {BORDER};">
                    <span style="color:{TEXT}; font-weight:600;">{species}</span>
                    <span style="color:{ACCENT}; font-weight:800;">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("System Configs"):
        is_custom = st.toggle("Manual Override: Recipient Email", value=False)
        target_email = st.text_input("Alert Destination", value="agiridhar41@gmail.com") if is_custom else "agiridhar41@gmail.com"
        threshold = st.slider("Population Alert Threshold", 1, 50, 5)
        if st.button("Reset Session Data", use_container_width=True):
            st.session_state.inventory = {}
            st.session_state.emails_sent = []
            st.rerun()

# ── Email Automation Trigger ────────────────────────────────
for species, count in st.session_state.inventory.items():
    if count >= threshold and species not in st.session_state.emails_sent:
        with st.spinner(f"Sending alert for {species}..."):
            if send_email_alert(species, count, target_email):
                st.session_state.emails_sent.append(species)
                st.success(f"📧 Alert Sent: {species} population is high.")
