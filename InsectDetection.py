import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Detection | TSA 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Inventory & Alert Logic ───────────────────────────────
# Initialize inventory in session state if it doesn't exist
if "inventory" not in st.session_state:
    st.session_state.inventory = {}
if "last_processed" not in st.session_state:
    st.session_state.last_processed = None

ALERT_THRESHOLD = 20

def add_to_inventory(label):
    # Only count valid insect detections
    if label not in ["No Specimen Detected", "Scanning...", "Awaiting Data"]:
        # Use a simple lock mechanism to prevent double-counting on reruns
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1

# ── Theme State & Toggle ──────────────────────────────────
t_col1, t_col2 = st.columns([8, 1.5])
with t_col2:
    dark_mode = st.toggle("Light/Dark Mode", value=True)

# ── Dynamic Earthy Color Palette ──────────────────────────
EARTH_BROWN = "#3B2F2F" 

if dark_mode:
    BG, CARD, TEXT = "#121412", "#26221C", "#E0E4E0"
    TEXT_DIM, ACCENT, BORDER = "#8AA38D", "#4CAF50", "#3D362E"
else:
    BG, CARD, TEXT = "#F4F7F4", "#F5E6D3", "#1B2E1B"
    TEXT_DIM, ACCENT, BORDER = "#5D574F", "#2E8B57", "#D9C5B2"

# ── CSS Overrides ─────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-image: none !important; background-color: {BG} !important; }}
    .main, [data-testid="stAppViewContainer"] {{ background-color: {BG} !important; font-family: 'Inter', sans-serif !important; }}
    label, [data-testid="stWidgetLabel"] p {{ color: {TEXT} !important; font-weight: 600 !important; }}

    /* Earthy Toggle & Tabs */
    div[role="switch"] {{ background-color: {EARTH_BROWN} !important; border: 1px solid {BORDER} !important; }}
    div[role="switch"][aria-checked="true"] {{ background-color: {ACCENT} !important; }}
    div[data-baseweb="tab-highlight"] {{ background-color: {ACCENT} !important; }}
    button[data-baseweb="tab"] {{ color: {TEXT_DIM} !important; border: none !important; }}
    button[aria-selected="true"] {{ color: {TEXT} !important; font-weight: 700 !important; }}

    /* Bento Elements */
    .bento-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem; font-weight: 700; color: {ACCENT} !important; margin-bottom: 8px; }}
    
    /* Alert Styling */
    .alert-box {{ 
        background-color: #721c24; color: #f8d7da; border-radius: 12px; 
        padding: 15px; border-left: 5px solid #f5c6cb; margin-bottom: 20px;
        font-weight: 600; animation: pulse 2s infinite;
    }}
    @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
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

# ── Alert Banner ──
for species, count in st.session_state.inventory.items():
    if count >= ALERT_THRESHOLD:
        st.markdown(f"""
            <div class="alert-box">
                ⚠️ CRITICAL THRESHOLD REACHED: {species.replace('_',' ').title()} population at {count}. 
                Automated alert sent to Pest Control / Environmental Agency.
            </div>
        """, unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    tabs = st.tabs(["Camera Control", "Manual Upload"])
    
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        auto_poll = st.toggle("Enable Auto-Analysis Loop", value=False)
        if cam_image:
            img = PIL.Image.open(cam_image)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)
        if auto_poll:
            time.sleep(3)
            st.rerun()
    
    with tabs[1]:
        up = st.file_uploader("Upload Image", type=["jpg","png"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Run Intelligence Engine"):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

with col_right:
    st.markdown('<p class="eyebrow">Result Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    display_label = label.replace('_', ' ').title()
    
    # Identification Card
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Identification</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">{display_label}</div>
            <div style="background: {BORDER}; height: 8px; border-radius: 10px; margin-top: 1.5rem; overflow: hidden;">
                <div style="background: {ACCENT}; width: {conf*100}%; height: 100%;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; margin-top: 10px;">Confidence: {conf:.2%}</p>
        </div>
    """, unsafe_allow_html=True)

    # Inventory Card
    st.markdown(f'<div class="bento-card"><p class="eyebrow">Live Inventory Tracking</p>', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.write("No specimens logged yet.")
    else:
        for bug, count in st.session_state.inventory.items():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; color:{TEXT}; border-bottom:1px solid {BORDER}; padding:5px 0;">
                    <span>{bug.replace('_',' ').title()}</span>
                    <span style="font-weight:bold; color:{ACCENT if count < ALERT_THRESHOLD else '#ff4b4b'}">{count}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──
st.markdown(f"""<div style="margin-top:2rem; text-align:center; color:{TEXT_DIM}; font-size:0.8rem; border-top:1px solid {BORDER}; padding-top:1rem;">TSA 2026 | TEAM ID: 2043-901</div>""", unsafe_allow_html=True)
