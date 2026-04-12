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

# ── Initialize Session State (BEFORE any UI) ───────────────
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "emails_sent" not in st.session_state:
    st.session_state.emails_sent = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "reset_confirmed" not in st.session_state:
    st.session_state.reset_confirmed = False

# ── Color Palettes (LOCKED, no re-evaluate) ───────────────
EARTH_BROWN = "#3B2F2F"
DARK_PALETTE = {
    "BG": "#121412",
    "CARD": "#26221C",
    "TEXT": "#E0E4E0",
    "TEXT_DIM": "#8AA38D",
    "ACCENT": "#4CAF50",
    "BORDER": "#3D362E"
}
LIGHT_PALETTE = {
    "BG": "#F4F7F4",
    "CARD": "#F5E6D3",
    "TEXT": "#1B2E1B",
    "TEXT_DIM": "#5D574F",
    "ACCENT": "#2E8B57",
    "BORDER": "#D9C5B2"
}

# Get colors ONCE per session
colors = DARK_PALETTE if st.session_state.dark_mode else LIGHT_PALETTE
BG, CARD, TEXT, TEXT_DIM, ACCENT, BORDER = (
    colors["BG"], colors["CARD"], colors["TEXT"], colors["TEXT_DIM"], colors["ACCENT"], colors["BORDER"]
)

# ── CSS Overrides + Animations ──────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');
    
    /* === ANIMATIONS === */
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 0px {ACCENT}; }}
        50% {{ box-shadow: 0 0 8px {ACCENT}66; }}
    }}
    
    @keyframes shake {{
        0%, 100% {{ transform: translateX(0); }}
        25% {{ transform: translateX(-4px); }}
        75% {{ transform: translateX(4px); }}
    }}
    
    /* === GLOBAL === */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-image: none !important; background-color: {BG} !important; }}
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        font-family: 'Inter', sans-serif !important;
        animation: fadeIn 0.4s ease-in;
    }}
    
    /* === CARDS === */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px;
        animation: slideIn 0.5s ease-out;
        transition: all 0.3s ease;
    }}
    
    .bento-card:hover {{
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }}
    
    /* === EYEBROW === */
    .eyebrow {{ 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-size: 0.7rem; 
        font-weight: 700; 
        color: {ACCENT} !important; 
        margin-bottom: 8px;
        animation: fadeIn 0.6s ease-out;
    }}
    
    /* === TOGGLE SWITCH === */
    div[role="switch"] {{ 
        background-color: {EARTH_BROWN} !important; 
        border: 1px solid {BORDER} !important;
        transition: all 0.3s ease !important;
    }}
    div[role="switch"][aria-checked="true"] {{ 
        background-color: {ACCENT} !important;
        box-shadow: 0 0 8px {ACCENT}44 !important;
    }}
    
    /* === SLIDER (NO RED) === */
    div[data-baseweb="slider"] [role="slider"] {{
        background-color: {ACCENT} !important;
        box-shadow: none !important;
        border: 2px solid {TEXT} !important;
        transition: all 0.2s ease !important;
    }}
    div[data-baseweb="slider"] [role="slider"]:hover, 
    div[data-baseweb="slider"] [role="slider"]:active, 
    div[data-baseweb="slider"] [role="slider"]:focus {{
        background-color: {TEXT} !important;
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 10px {ACCENT}44 !important;
        outline: none !important;
    }}
    
    /* Track */
    div[data-baseweb="slider"] > div > div {{ 
        background: {BORDER} !important;
    }}
    div[data-baseweb="slider"] div[data-testid="stTickBar"] + div > div > div:first-child {{
        background-color: {ACCENT} !important;
    }}
    
    /* === BUTTONS === */
    button {{
        transition: all 0.2s ease !important;
    }}
    button:active {{
        transform: scale(0.97);
    }}
    
    /* === THRESHOLD ALERT === */
    .alert-threshold {{
        animation: glow 1.5s ease-in-out infinite;
    }}
    
    /* === DANGER BUTTON === */
    .danger-btn {{
        animation: shake 0.4s ease-in-out;
    }}
    
</style>
""", unsafe_allow_html=True)

# ── Inventory & Email Configuration ───────────────────────
def send_pest_control_email(species, count, receiver_email, threshold):
    sender = "aniyuva745@gmail.com"
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
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
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

# Theme toggle at top
t_col1, t_col2 = st.columns([8, 1.5])
with t_col2:
    if st.toggle("Light/Dark Mode", value=st.session_state.dark_mode):
        if not st.session_state.dark_mode:
            st.session_state.dark_mode = True
            st.rerun()
    else:
        if st.session_state.dark_mode:
            st.session_state.dark_mode = False
            st.rerun()

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
        
        st.markdown("<hr style='opacity:0.2; margin: 15px 0;'>", unsafe_allow_html=True)
        
        # Reset inventory button
        col_reset_label, col_reset_btn = st.columns([1, 1])
        with col_reset_label:
            st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.8rem; margin-top: 8px;'>Reset Data</p>", unsafe_allow_html=True)
        with col_reset_btn:
            if st.button("🔄 Clear", use_container_width=True, key="reset_btn"):
                st.session_state.reset_confirmed = True
        
        # Confirmation dialog
        if st.session_state.reset_confirmed:
            st.markdown(f"<p style='color:#E74C3C; font-size:0.8rem; font-weight:600;'>⚠️ Sure? Clears all inventory.</p>", unsafe_allow_html=True)
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Yes", use_container_width=True, key="confirm_yes"):
                    st.session_state.inventory = {}
                    st.session_state.emails_sent = []
                    st.session_state.reset_confirmed = False
                    st.toast("✅ Inventory cleared!", icon="✅")
                    st.rerun()
            with col_no:
                if st.button("❌ No", use_container_width=True, key="confirm_no"):
                    st.session_state.reset_confirmed = False
                    st.rerun()
        
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
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        
        upload_mode = st.radio("Upload mode", ["Single", "Batch"], horizontal=True, label_visibility="collapsed")
        
        if upload_mode == "Single":
            up = st.file_uploader("Upload Image", type=["jpg","png"], label_visibility="collapsed", key="single_upload")
            if up:
                img = PIL.Image.open(up)
                st.image(img, use_container_width=True)
                if st.button("Run Intelligence Engine"):
                    label, conf = classify(img)
                    st.session_state.insect_res = (label, conf)
                    add_to_inventory(label, target_email, current_threshold)
        else:
            uploads = st.file_uploader("Upload multiple images", type=["jpg","png"], accept_multiple_files=True, label_visibility="collapsed", key="batch_upload")
            if uploads:
                st.markdown(f"<p style='color:{TEXT_DIM}; font-size:0.8rem;'><strong>{len(uploads)}</strong> images selected</p>", unsafe_allow_html=True)
                if st.button("🔍 Process All", use_container_width=True):
                    progress_bar = st.progress(0)
                    results_list = []
                    
                    for idx, up in enumerate(uploads):
                        try:
                            img = PIL.Image.open(up)
                            label, conf = classify(img)
                            st.session_state.insect_res = (label, conf)
                            add_to_inventory(label, target_email, current_threshold)
                            results_list.append({"file": up.name, "species": label, "confidence": f"{conf:.2%}"})
                        except Exception as e:
                            results_list.append({"file": up.name, "species": "Error", "confidence": str(e)})
                        
                        progress_bar.progress((idx + 1) / len(uploads))
                    
                    st.success(f"✅ Processed {len(uploads)} images")
                    with st.expander("📋 View results"):
                        for res in results_list:
                            st.markdown(f"**{res['file']}** → {res['species']} ({res['confidence']})")
        
        st.markdown('</div>', unsafe_allow_html=True)

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
        # Show total count
        total = sum(st.session_state.inventory.values())
        st.markdown(f"<p style='color:{ACCENT}; font-weight:700; font-size:1.1rem;'>Total: {total}</p>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2; margin: 8px 0;'>", unsafe_allow_html=True)
        
        for species, count in st.session_state.inventory.items():
            is_over = count >= current_threshold
            color = "#ff4b4b" if is_over else TEXT
            alert_class = "alert-threshold" if is_over else ""
            st.markdown(f"""<div style="display:flex; justify-content:space-between; color:{color}; padding: 6px 0;" class="{alert_class}">
                <span>{species.replace('_',' ').title()}</span><span style="font-weight:700;">{count}</span></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f'<p style="text-align:center; color:{TEXT_DIM}; font-size:0.7rem;">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)
