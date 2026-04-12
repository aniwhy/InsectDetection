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

# ── Theme Toggle ──────────────────────────────────────────
# Initialize theme state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ── Color Palettes (Locked Per Mode) ──────────────────────
def get_colors(dark: bool):
    if dark:
        return {
            "bg": "#0F0F0F",
            "surface": "#1A1A1A",
            "card": "#252525",
            "text": "#F0F0F0",
            "text_dim": "#A8A8A8",
            "accent": "#2ECC71",
            "accent_dark": "#27AE60",
            "border": "#3A3A3A",
            "error": "#E74C3C",
            "hover_bg": "#2F2F2F"
        }
    else:
        return {
            "bg": "#FAFBF8",
            "surface": "#F4F6F2",
            "card": "#FFFFFF",
            "text": "#1F2E1F",
            "text_dim": "#5B6B5B",
            "accent": "#2ECC71",
            "accent_dark": "#27AE60",
            "border": "#D4E0D4",
            "error": "#C0392B",
            "hover_bg": "#EEF2EC"
        }

colors = get_colors(st.session_state.dark_mode)

# ── CSS: Aggressive Overrides ────────────────────────────
css_overrides = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');

/* === GLOBAL RESETS === */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {{
    background-color: {colors['bg']} !important;
    color: {colors['text']} !important;
}}

/* Hide header/footer */
[data-testid="stHeader"], header, footer {{
    display: none !important;
}}

.appViewContainer {{
    background-color: {colors['bg']} !important;
}}

/* === TYPOGRAPHY === */
* {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

h1, h2, h3, .title {{
    font-family: 'Playfair Display', serif !important;
    color: {colors['text']} !important;
}}

/* === TEXT ELEMENTS === */
p, span, div, label {{
    color: {colors['text']} !important;
}}

/* === INPUTS & BUTTONS === */
/* Text input */
input[type="text"], input[type="email"], input[type="password"], textarea {{
    background-color: {colors['card']} !important;
    color: {colors['text']} !important;
    border: 1px solid {colors['border']} !important;
    border-radius: 8px !important;
}}

input[type="text"]:focus, input[type="email"]:focus, textarea:focus {{
    background-color: {colors['surface']} !important;
    border-color: {colors['accent']} !important;
    box-shadow: 0 0 0 3px {colors['accent']}22 !important;
    outline: none !important;
}}

/* Placeholder text */
input::placeholder, textarea::placeholder {{
    color: {colors['text_dim']} !important;
    opacity: 1 !important;
}}

/* === STREAMLIT BUTTONS === */
button, [role="button"] {{
    background-color: {colors['accent']} !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}

button:hover, [role="button"]:hover {{
    background-color: {colors['accent_dark']} !important;
    box-shadow: 0 4px 12px {colors['accent']}33 !important;
}}

button:active, [role="button"]:active {{
    transform: scale(0.98);
}}

/* === TOGGLE SWITCHES === */
div[role="switch"] {{
    background-color: {colors['border']} !important;
    border: 1px solid {colors['border']} !important;
}}

div[role="switch"][aria-checked="true"] {{
    background-color: {colors['accent']} !important;
    border-color: {colors['accent']} !important;
}}

/* === SLIDER (Heavy Fix) === */
div[data-baseweb="slider"] {{
    background-color: transparent !important;
}}

/* Slider track */
div[data-baseweb="slider"] > div > div {{
    background-color: {colors['border']} !important;
}}

/* Slider thumb */
div[data-baseweb="slider"] [role="slider"] {{
    background-color: {colors['accent']} !important;
    border: 2px solid {colors['accent']} !important;
    box-shadow: none !important;
}}

div[data-baseweb="slider"] [role="slider"]:hover,
div[data-baseweb="slider"] [role="slider"]:focus,
div[data-baseweb="slider"] [role="slider"]:active {{
    background-color: {colors['accent_dark']} !important;
    border-color: {colors['accent_dark']} !important;
    box-shadow: 0 0 0 8px {colors['accent']}22 !important;
    outline: none !important;
}}

/* Filled portion of slider */
div[data-baseweb="slider"] div[style*="background"] {{
    background-color: {colors['accent']} !important;
}}

/* === TABS === */
[data-baseweb="tab-list"] {{
    border-bottom: 1px solid {colors['border']} !important;
}}

[data-baseweb="tab"] {{
    color: {colors['text_dim']} !important;
}}

[data-baseweb="tab"][aria-selected="true"] {{
    color: {colors['accent']} !important;
    border-bottom-color: {colors['accent']} !important;
}}

/* === FILE UPLOADER === */
[data-testid="stFileUploadDropzone"] {{
    border: 2px dashed {colors['border']} !important;
    background-color: {colors['surface']} !important;
}}

[data-testid="stFileUploadDropzone"]:hover {{
    border-color: {colors['accent']} !important;
    background-color: {colors['hover_bg']} !important;
}}

/* === CONTAINERS & CARDS === */
.stContainer, [data-testid="column"], [data-testid="element-container"] {{
    background-color: transparent !important;
}}

.bento-card {{
    background-color: {colors['card']} !important;
    border: 1px solid {colors['border']} !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}}

/* === LABELS & EYEBROWS === */
.eyebrow {{
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 0.65rem;
    font-weight: 700;
    color: {colors['accent']} !important;
    margin-bottom: 12px;
    display: block;
}}

/* === HORIZONTAL RULES === */
hr {{
    border-color: {colors['border']} !important;
    opacity: 1 !important;
}}

/* === CAMERA INPUT === */
[data-testid="camera_input_container"] {{
    background-color: {colors['surface']} !important;
    border: 1px solid {colors['border']} !important;
    border-radius: 8px !important;
}}

/* === TOAST/ALERTS === */
.stAlert {{
    background-color: {colors['surface']} !important;
    border: 1px solid {colors['border']} !important;
    color: {colors['text']} !important;
    border-radius: 8px !important;
}}

/* === SELECT BOXES === */
[data-baseweb="select"] {{
    background-color: {colors['card']} !important;
    border-color: {colors['border']} !important;
}}

[data-baseweb="select"]:hover {{
    border-color: {colors['accent']} !important;
}}

/* === SCROLLBAR === */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background-color: {colors['surface']} !important;
}}

::-webkit-scrollbar-thumb {{
    background-color: {colors['border']} !important;
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background-color: {colors['text_dim']} !important;
}}

/* === OVERRIDE STREAMLIT RED === */
/* Kill all red/pink defaults */
.stAlert, [class*="alert"], [class*="error"], [class*="warning"] {{
    --alert-bg: {colors['surface']} !important;
    --alert-border: {colors['border']} !important;
    --alert-text: {colors['text']} !important;
}}

/* Target any red-colored element Streamlit tries to inject */
[style*="background-color: #f"] {{
    background-color: {colors['card']} !important;
}}

[style*="color: #f"] {{
    color: {colors['accent']} !important;
}}

</style>
"""

st.markdown(css_overrides, unsafe_allow_html=True)

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
                st.toast(f"✅ Alert sent to {target_email}", icon="✅")
            else:
                st.toast("⚠️ Email failed. Check App Password.", icon="⚠️")

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
# Header with theme toggle
header_col1, header_col2 = st.columns([8, 1.5])

with header_col1:
    st.markdown(f'<h1 style="font-family: Playfair Display; color: {colors["text"]}; margin: 0; font-size: 2.8rem;">Insect Detection</h1>', unsafe_allow_html=True)

with header_col2:
    if st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode):
        if not st.session_state.dark_mode:
            st.session_state.dark_mode = True
            st.rerun()
    else:
        if st.session_state.dark_mode:
            st.session_state.dark_mode = False
            st.rerun()

# Main layout
col_left, col_right = st.columns([1.5, 1], gap="medium")

# ── LEFT COLUMN: Data Intake ──────────────────────────────
with col_left:
    st.markdown(f'<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📷 Camera", "📁 Upload"])
    
    with tabs[0]:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        cam_active = st.toggle("Activate Live Feed", value=True, key="cam_toggle")
        if cam_active:
            cam_image = st.camera_input("Take snapshot", label_visibility="collapsed")
            if cam_image:
                img = PIL.Image.open(cam_image)
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, st.session_state.get("target_email", "agiridhar41@gmail.com"), st.session_state.get("threshold", 5))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown('<div class="bento-card">', unsafe_allow_html=True)
        up = st.file_uploader("Choose image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True, caption="Uploaded Image")
            if st.button("🔍 Run Classification", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label, st.session_state.get("target_email", "agiridhar41@gmail.com"), st.session_state.get("threshold", 5))
        st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT COLUMN: Config + Results ───────────────────────
with col_right:
    # Configuration card
    st.markdown(f'<p class="eyebrow">Agency Configuration</p>', unsafe_allow_html=True)
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    
    is_custom = st.toggle("Custom Judge Email", value=False, key="email_toggle")
    if is_custom:
        target_email = st.text_input("Recipient Email", placeholder="judge@example.com", label_visibility="collapsed")
        st.session_state.target_email = target_email
    else:
        target_email = "agiridhar41@gmail.com"
        st.markdown(f"<p style='color: {colors['text_dim']}; font-size: 0.8rem;'>Default: <strong>{target_email}</strong></p>", unsafe_allow_html=True)
        st.session_state.target_email = target_email
    
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: {colors['text_dim']}; font-size: 0.8rem; margin: 10px 0;'><strong>Alert Threshold</strong></p>", unsafe_allow_html=True)
    current_threshold = st.slider("Specimens", min_value=1, max_value=50, value=5, label_visibility="collapsed")
    st.session_state.threshold = current_threshold
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results card
    st.markdown(f'<p class="eyebrow">Result Engine</p>', unsafe_have_html=True)
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    display_label = label.replace('_', ' ').title()
    
    st.markdown(f"""
    <div>
        <p class="eyebrow">Identification</p>
        <div style="font-family: Playfair Display; font-size: 2.4rem; color: {colors['text']}; font-weight: 700; margin: 10px 0;">{display_label}</div>
        <p style="color: {colors['text_dim']}; font-size: 0.85rem; margin: 8px 0; font-weight: 500;">Confidence: <strong style="color: {colors['accent']};">{conf:.1%}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    
    # Inventory
    st.markdown(f"<p class='eyebrow'>Population Inventory</p>", unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<p style='color: {colors['text_dim']}; font-size: 0.9rem;'>No specimens logged.</p>", unsafe_allow_html=True)
    else:
        for species, count in sorted(st.session_state.inventory.items()):
            is_over = count >= current_threshold
            species_name = species.replace('_', ' ').title()
            indicator_color = colors['error'] if is_over else colors['accent']
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid {colors['border']};">
                <span style="color: {colors['text']}; font-weight: 500;">{species_name}</span>
                <span style="color: {indicator_color}; font-weight: 700; font-size: 1.1rem;">{count}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f'<p style="text-align: center; color: {colors["text_dim"]}; font-size: 0.75rem; margin-top: 40px; padding: 20px 0; border-top: 1px solid {colors["border"]};">TSA 2026 | TEAM 2043-901</p>', unsafe_allow_html=True)
