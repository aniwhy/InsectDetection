import streamlit as st
from ultralytics import YOLO
import PIL.Image
import os
import time
import smtplib
from email.message import EmailMessage

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="InvasiveGuard | TSA 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Invasive Status Database ──────────────────────────────
# I have added the specific invasive species from IP102 here
INSECT_DATABASE = {
    "Ant": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Native ecological scavenger; essential for soil aeration."},
    "Aphid": {"status": "Invasive", "color": "#FF4B4B", "desc": "Sucking insect that transmits plant viruses and stunting."},
    "Armyworm": {"status": "Invasive", "color": "#FF4B4B", "desc": "High-density agricultural pest known for rapid defoliation."},
    "Bee": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Critical native pollinator protected under conservation guidelines."},
    "Beetle": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Common native species contributing to nutrient cycling."},
    "Borer": {"status": "Invasive", "color": "#FF4B4B", "desc": "Larval pest that destroys vascular plant tissue from within."},
    "Butterfly": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Indicator species for local environmental health."},
    "Dragonfly": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Beneficial predator that controls local mosquito populations."},
    "Fly": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Common diptera species; generally non-threatening to crops."},
    "Grasshopper": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Local herbivore; monitored for population surges."},
    "Ladybug": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Beneficial predator used in Integrated Pest Management (IPM)."},
    "Lantern Fly": {"status": "Invasive", "color": "#FF4B4B", "desc": "Aggressive invasive species threatening timber and grapes."},
    "Mosquito": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Local nuisance species; vector monitoring recommended."},
    "Spider": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Generalist predator essential for natural pest control."},
    "Wasp": {"status": "Non-Invasive", "color": "#4CAF50", "desc": "Natural predator of caterpillars and garden pests."}
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
    CARD_BG = "rgba(30, 35, 30, 0.4)" 
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#E0E4E0", "#8AA38D", "#4CAF50", "#2D362E", "#1A1D1A"
    GLOW = "rgba(76, 175, 80, 0.15)"
else:
    BG_GRADIENT = "linear-gradient(135deg, #F5F9F5 0%, #E8EEE8 100%)"
    CARD_BG = "rgba(255, 255, 255, 0.95)"
    TEXT, TEXT_DIM, ACCENT, BORDER, SURFACE = "#1B2E1B", "#4A5D4C", "#2E8B57", "#C2D9C5", "#FFFFFF"
    GLOW = "rgba(0, 0, 0, 0.05)"

# ── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .main, [data-testid="stAppViewContainer"] {{ background: {BG_GRADIENT} !important; font-family: 'Inter', sans-serif !important; }}
    .bento-card {{ background: {CARD_BG} !important; backdrop-filter: blur(12px); border: 1px solid {BORDER}; border-radius: 24px; padding: 24px; margin-bottom: 20px; transition: all 0.4s; }}
    .bento-card:hover {{ transform: translateY(-4px); border-color: {ACCENT}; box-shadow: 0 12px 30px {GLOW}; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: 3px; font-size: 0.7rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    .stButton > button {{ border-radius: 14px !important; background-color: {SURFACE} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Logic Functions ───────────────────────────────────────
@st.cache_resource
def load_model():
    # Loading your custom 15-class model
    return YOLO('largedata.pt') 

model = load_model()

def classify(img):
    results = model.predict(source=img, conf=0.45, verbose=False)
    if results[0].probs is not None:
        class_id = int(results[0].probs.top1)
        raw_label = model.names[class_id]
        
        # CLEANUP LOGIC: This ensures "Asiatic_Rice_Borer" becomes "Borer" 
        # to match your database cards perfectly.
        if "Borer" in raw_label: label = "Borer"
        elif "Armyworm" in raw_label: label = "Armyworm"
        elif "Aphid" in raw_label: label = "Aphid"
        else: label = raw_label.replace("_", " ").title()
        
        conf = float(results[0].probs.top1conf)
        return label, conf
    return "No Specimen Detected", 0.0

def add_to_inventory(label):
    if label not in ["No Specimen Detected", "Awaiting Data"]:
        st.session_state.inventory[label] = st.session_state.inventory.get(label, 0) + 1
        st.toast(f"Log Updated: {label}", icon="🐞")

# ── UI Layout ─────────────────────────────────────────────
t_col1, t_col2, t_col3 = st.columns([1, 8, 1])
with t_col2:
    st.markdown(f'<div style="text-align:center; padding: 40px 0;"><h1 style="font-family:\'Playfair Display\'; font-size: 4rem; color:{TEXT};">InvasiveGuard</h1><p style="color:{ACCENT}; font-weight:700; letter-spacing:5px;">TSA 2026 | ENGINEERING DESIGN</p></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown('<p class="eyebrow">Visual Analysis</p>', unsafe_allow_html=True)
    tabs = st.tabs(["LIVE CAMERA", "DATA UPLOAD"])
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        if cam_image:
            label, conf = classify(PIL.Image.open(cam_image))
            st.session_state.insect_res = (label, conf)
            add_to_inventory(label)
    with tabs[1]:
        up = st.file_uploader("Upload", type=["jpg","png"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Run Diagnostic", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

with col_right:
    label, conf = st.session_state.insect_res
    info = INSECT_DATABASE.get(label, {"status": "Safe", "color": ACCENT, "desc": "Awaiting specimen for identification..."})
    
    st.markdown(f"""
        <div class="bento-card" style="border-right: 6px solid {info['color']};">
            <p class="eyebrow">Result</p>
            <div style="font-family:'Playfair Display'; font-size: 2.8rem; color:{TEXT};">{label}</div>
            <div style="background:{info['color']}22; color:{info['color']}; padding:4px 12px; border-radius:8px; display:inline-block; font-weight:900; margin: 10px 0;">{info['status'].upper()}</div>
            <p style="color:{TEXT_DIM}; font-size:0.9rem;">{info['desc']}</p>
            <div style="display:flex; justify-content:space-between; margin-top:20px;">
                <span style="color:{TEXT_DIM};">Match Probability</span>
                <span style="color:{ACCENT}; font-weight:900;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Local Inventory</p>', unsafe_allow_html=True)
    st.markdown('<div class="bento-card">', unsafe_allow_html=True)
    for species, count in st.session_state.inventory.items():
        st.markdown(f'<div style="display:flex; justify-content:space-between; border-bottom:1px solid {BORDER}; padding: 5px 0;"><span style="color:{TEXT};">{species}</span><span style="color:{ACCENT}; font-weight:800;">{count}</span></div>', unsafe_allow_html=True)
    if not st.session_state.inventory: st.write("No detections logged.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Dynamic Reference Grid ──
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown('<p class="eyebrow" style="text-align:center;">Biological Database Reference</p>', unsafe_allow_html=True)

ref_items = list(INSECT_DATABASE.items())
for i in range(0, len(ref_items), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(ref_items):
            name, data = ref_items[i+j]
            with cols[j]:
                st.markdown(f"""
                    <div class="bento-card" style="border-left: 4px solid {data['color']}; min-height:150px;">
                        <div style="color:{data['color']}; font-size:0.6rem; font-weight:900;">{data['status'].upper()}</div>
                        <div style="font-family:'Playfair Display'; font-size:1.4rem; color:{TEXT};">{name}</div>
                        <div style="color:{TEXT_DIM}; font-size:0.8rem; margin-top:8px;">{data['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
