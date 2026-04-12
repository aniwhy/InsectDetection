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

# ── Inventory & Email Configuration ───────────────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []

def send_pest_control_email(species, count, receiver_email, threshold):
    sender = "aniyuva745@gmail.com"
    # Ensure this is a Google 'App Password', not your login password
    password = "crei kema pjwg djwl" 
    
    subject = f"TSA ALERT: Population Threshold Reached ({species.title()})"
    body = f"""
    The Automated Insect Population Counter has detected a population influx.
    
    Species identified: {species.replace('_', ' ').title()}
    Total count: {count}
    User-defined Threshold: {threshold}
    Location: Seven Springs, PA (TSA 2026)
    
    This notification was routed to: {receiver_email}
    """
    
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Using SSL port 465 for better compatibility
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}") # Debugging
        return False

def add_to_inventory(label, target_email, threshold):
    invalid_labels = ["No Specimen Detected", "Scanning...", "Awaiting Data", "Scanning"]
    if label not in invalid_labels:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        count = st.session_state.inventory[label]
        
        if count >= threshold and label not in st.session_state.emails_sent:
            if send_pest_control_email(label, count, target_email, threshold):
                st.session_state.emails_sent.append(label)
                st.toast(f"Email Alert Sent to {target_email}!", icon="✅")
            else:
                st.toast("Email failed to send. Check App Password.", icon="⚠️")

# ── Theme Logic ──────────────────────────────────────────
t_col1, t_col2 = st.columns([8, 1.5])
with t_col2:
    dark_mode = st.toggle("Light/Dark Mode", value=True)

EARTH_BROWN = "#3B2F2F" 
if dark_mode:
    BG, CARD, TEXT, TEXT_DIM, ACCENT, BORDER = "#121412", "#26221C", "#E0E4E0", "#8AA38D", "#4CAF50", "#3D362E"
else:
    BG, CARD, TEXT, TEXT_DIM, ACCENT, BORDER = "#F4F7F4", "#F5E6D3", "#1B2E1B", "#5D574F", "#2E8B57", "#D9C5B2"

# ── CSS Overrides (Heavy Duty Slider Fix) ─────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-image: none !important; background-color: {BG} !important; }}
    .main, [data-testid="stAppViewContainer"] {{ background-color: {BG} !important; font-family: 'Inter', sans-serif !important; }}
    
    /* Toggle Switch Styling */
    div[role="switch"] {{ background-color: {EARTH_BROWN} !important; border: 1px solid {BORDER} !important; }}
    div[role="switch"][aria-checked="true"] {{ background-color: {ACCENT} !important; }}
    
    /* THE ULTIMATE SLIDER FIX */
    /* Target the thumb and kill red on all states */
    div[data-baseweb="slider"] [role="slider"] {{
        background-color: {ACCENT} !important;
        box-shadow: none !important;
        border: 2px solid {TEXT} !important;
    }}
    div[data-baseweb="slider"] [role="slider"]:hover, 
    div[data-baseweb="slider"] [role="slider"]:active, 
    div[data-baseweb="slider"] [role="slider"]:focus {{
        background-color: {TEXT} !important;
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 10px {ACCENT}44 !important; /* Green glow, NOT red */
        outline: none !important;
    }}

    /* Track colors */
    div[data-baseweb="slider"] > div > div {{ background: {BORDER} !important; }}
    div[data-baseweb="slider"] div[data-testid="stTickBar"] + div > div > div:first-child {{
        background-color: {ACCENT} !important;
    }}

    .bento-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem; font-weight: 700; color: {ACCENT} !important; margin-bottom: 8px; }}
</style>
""", unsafe_allow_html=True)

# ── Model Logic ───────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('exp-2.pt')

model = load_model()

def classify(img):
    results = model.predict(img, verbose=False)
    if results and results[0].probs:
        conf = results[0].probs.top1conf.item()
        idx = results[0].probs.top1
        label = model.names[idx]
        if conf < 0.55: return "No Specimen Detected", conf
        return label, conf
    return "Scanning...", 0.0

# ── Main UI ───────────────────────────────────────────────
st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin-top:-40px;">Insect Detection</h1>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_right:
    st.markdown('<p class="eyebrow">Agency Configuration</p>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
        is_custom = st.toggle("Custom Judge Email", value=False)
        if is_custom:
            target_email = st.text_input("Recipient Email", placeholder="judge@example.com")
        else:
            target_email = "agiridhar41@gmail.com"
            st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.8rem;'>Default: {target_email}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='opacity:0.2; margin: 15px 0;'>", unsafe_allow_html=True)
        current_threshold = st.slider("Alert Threshold", min_value=1, max_value=50, value=5)
        st.markdown('</div>', unsafe_allow_html=True)

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    tabs = st.tabs(["Camera Control", "Manual Upload"])
    with tabs[0]:
        cam_active = st.toggle("Live Camera Feed", value=True)
        if cam_active:
            cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, target_email, current_threshold)
    with tabs[1]:
        up = st.file_uploader("Upload Image", type=["jpg","png"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Run Intelligence Engine"):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, target_email, current_threshold)

with col_right:
    st.markdown('<p class="eyebrow">Result Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    display_label = label.replace('_', ' ').title()
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Identification</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">{display_label}</div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; margin-top: 10px; font-weight: 600;">Confidence: {conf:.2%}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="bento-card"><p class="eyebrow">Population Inventory</p>', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color:{TEXT_DIM};'>No specimens logged.</p>", unsafe_allow_html=True)
    else:
        for species, count in st.session_state.inventory.items():
            is_over = count >= current_threshold
            color = "#ff4b4b" if is_over else TEXT
            st.markdown(f"""<div style="display:flex; justify-content:space-between; color:{color};">
                <span>{species.replace('_',' ').title()}</span><span>{count}</span></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f'<p style="text-align:center; color:{TEXT_DIM}; font-size:0.7rem;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)
