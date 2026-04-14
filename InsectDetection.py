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

# ── Insect Database & Status Mapping ──────────────────────
# Based on your dataset screenshot: 5 Invasive vs 4 Non-Invasive
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

# ── Theme Configuration ────────────────────────────────────
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
    .header-container {{ text-align: center; padding: 40px 0 20px 0; }}
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
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.75rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    .stButton > button {{ border-radius: 14px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; font-weight: 600 !important; }}
    .stButton > button:hover {{ background-color: {ACCENT}22 !important; border-color: {ACCENT} !important; color: {ACCENT} !important; }}
    .stMarkdown p, .stMarkdown span, label, .stSlider p, div[data-testid="stWidgetLabel"] p {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')  # Ensure your custom trained model path is here if not using default

model = load_model()

def get_status_info(label):
    key = label.lower().replace(" ", "_")
    return INSECT_DATABASE.get(key, {"status": "Unknown", "color": "#888888", "desc": "Non-indexed species"})

def classify(img):
    # This was the bug: it was hardcoded to "stem_borer".
    # Now it actually runs your model on the image.
    results = model(img)
    if results[0].probs is not None:
        idx = results[0].probs.top1
        label = results[0].names[idx]
        conf = float(results[0].probs.top1conf)
        return label, conf
    return "No Specimen Detected", 0.0

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Scanning...", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Logged: {label.replace('_', ' ').title()}", icon="🐞")

def send_email_alert(species, count, recipient):
    sender_email = "aniyuva745@gmail.com"
    sender_password = "xkoz kvqr xtjr atio"
    info = get_status_info(species)
    
    msg = EmailMessage()
    msg.set_content(f"""
    INVASIVE SPECIES ALERT
    ----------------------
    Status: {info['status']}
    Species: {species.replace('_', ' ').title()}
    Current Population Count: {count}
    System ID: TSA-2026-HQ
    """)
    msg['Subject'] = f"⚠️ ALERT: {species.title()} Threshold Reached"
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
    if st.button("☀️" if st.session_state.dark_mode else "🌙"):
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
            cam_image = st.camera_input("Image", label_visibility="collapsed")
            if cam_image:
                label, conf = classify(PIL.Image.open(cam_image))
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)
                if sync_active: time.sleep(2); st.rerun()
        else:
            st.info("Live feed disabled.")
    
    with tabs[1]:
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        upload_mode = st.radio("Processing Module", ["Single", "Batch"], horizontal=True)
        up = st.file_uploader("Select Image", type=["jpg","png"])
        if up and st.button("Run Classification"):
            label, conf = classify(PIL.Image.open(up))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<p class="eyebrow">Detection Metrics</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    
    info = get_status_info(label)
    
    st.markdown(f"""
        <div class="bento-card" style="border-left: 5px solid {info['color']};">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <p class="eyebrow" style="color:{TEXT_DIM}">Identified Insect</p>
                    <div style="font-family:'Playfair Display'; font-size: 2.5rem; color:{TEXT}; line-height:1.1;">
                        {label.replace('_', ' ').title()}
                    </div>
                </div>
                <div style="background:{info['color']}22; color:{info['color']}; padding:4px 10px; border-radius:8px; font-size:0.7rem; font-weight:800; border:1px solid {info['color']};">
                    {info['status'].upper()}
                </div>
            </div>
            <p style="color:{TEXT_DIM}; font-size:0.8rem; margin-top:10px;">{info['desc']}</p>
            <div style="display:flex; justify-content:space-between; margin-top:20px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.85rem; font-weight:600;">Confidence Rating</span>
                <span style="color:{ACCENT}; font-weight:800; font-size:1.2rem;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Inventory</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM}; font-style:italic;'>No specimens logged.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            inv_info = get_status_info(species)
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid {BORDER};">
                    <span style="color:{TEXT}; font-weight:600;">{species.replace('_', ' ').title()}</span>
                    <span style="color:{inv_info['color']}; font-weight:800;">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("System Configs"):
        target_email = st.text_input("Alert Destination", value="agiridhar41@gmail.com")
        threshold = st.slider("Population Alert Threshold", 1, 50, 5)
        if st.button("Reset Session Data", use_container_width=True):
            st.session_state.inventory = {}; st.session_state.emails_sent = []; st.rerun()

# ── Email Automation Trigger ────────────────────────────────
for species, count in st.session_state.inventory.items():
    if count >= threshold and species not in st.session_state.emails_sent:
        # Only alert for invasive species
        if get_status_info(species)['status'] == "Invasive":
            if send_email_alert(species, count, target_email):
                st.session_state.emails_sent.append(species)
                st.success(f"📧 Alert Sent for {species.title()}")
