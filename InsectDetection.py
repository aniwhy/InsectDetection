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
    
    /* Disable Text Copying */
    body, .stApp {{
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }}

    /* Re-enable selection for input fields */
    input, textarea {{
        user-select: text !important;
    }}

    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    
    .main, [data-testid="stAppViewContainer"] {{ 
        background: {BG_GRADIENT} !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    .bento-card {{ 
        background: {CARD_BG} !important; 
        backdrop-filter: blur(12px); 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
    }}
    .bento-card:hover {{
        transform: translateY(-4px);
        border-color: {ACCENT};
        box-shadow: 0 12px 30px {GLOW};
    }}

    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 8px; 
        margin-bottom: 16px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        background-color: {SURFACE};
        border-radius: 12px 12px 0 0;
        border: 1px solid {BORDER};
        transition: 0.3s;
        flex-grow: 1;
    }}
    .stTabs [data-baseweb="tab"] div {{ 
        color: {TEXT_DIM} !important; 
        font-weight: 600;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {ACCENT} !important; }}
    .stTabs [aria-selected="true"] div {{ 
        color: white !important; 
        font-weight: 700; 
        font-size: 0.9rem;
    }}

    .eyebrow {{ text-transform: uppercase; letter-spacing: 3px; font-size: 0.7rem; font-weight: 800; color: {ACCENT}; margin-bottom: 12px; }}
    
    .stButton > button {{ 
        border-radius: 14px !important; 
        background-color: {SURFACE} !important; 
        color: {TEXT} !important; 
        border: 1px solid {BORDER} !important;
        transition: 0.3s !important;
    }}
    .stButton > button:hover {{ transform: scale(1.02); border-color: {ACCENT} !important; }}

    /* Fix input label visibility */
    .stMarkdown p, label, .stSlider div {{ color: {TEXT} !important; }}
    
    /* Improve tab content spacing */
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 20px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
t_col1, t_col2, t_col3 = st.columns([1, 8, 1])

with t_col2:
    st.markdown(f"""
        <div style="text-align:center; padding: 40px 0 20px 0; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;">
            <h1 style="font-family:'Playfair Display'; font-size: 4.8rem; margin:0; line-height:1; color:{TEXT}; user-select: none; pointer-events: none;">Insect Detection</h1>
            <p style="color:{ACCENT}; font-size:0.8rem; font-weight:700; letter-spacing:5px; margin-top:15px; opacity:0.8; user-select: none; pointer-events: none;">
                TSA 2026 &nbsp; | &nbsp; ENGINEERING DESIGN &nbsp; | &nbsp; TEAM 2043-901
            </p>
        </div>
    """, unsafe_allow_html=True)

with t_col3:
    st.write(" ") 
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

# ── UI Layout ─────────────────────────────────────────────
col_left, col_right = st.columns([1.6, 1], gap="large")

with col_left:
    st.markdown('<p class="eyebrow">Input Channels</p>', unsafe_allow_html=True)
    tabs = st.tabs(["📷 LIVE FEED", "📤 UPLOAD"])
    
    with tabs[0]:
        st.session_state.cam_enabled = st.toggle("Enable Camera System", value=st.session_state.cam_enabled)
        if st.session_state.cam_enabled:
            cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
            if cam_image:
                label, conf = classify(PIL.Image.open(cam_image))
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

    with tabs[1]:
        up = st.file_uploader("Drop Image", type=["jpg","png"], label_visibility="collapsed")
        if up:
            img = PIL.Image.open(up)
            st.image(img, use_container_width=True)
            if st.button("Analyze Image", use_container_width=True):
                label, conf = classify(img)
                st.session_state.insect_res = (label, conf)
                add_to_inventory(label)

with col_right:
    st.markdown('<p class="eyebrow">Detection Analysis</p>', unsafe_allow_html=True)
    label, conf = st.session_state.insect_res
    info = INSECT_DATABASE.get(label, {"status": "Unknown", "color": ACCENT, "desc": "Awaiting classification..."})
    
    st.markdown(f"""
        <div class="bento-card" style="border-right: 6px solid {info['color']};">
            <p class="eyebrow" style="color:{TEXT_DIM}; font-size:0.6rem;">Species Identified</p>
            <div style="font-family:'Playfair Display'; font-size: 2.8rem; color:{TEXT}; line-height:1; margin-bottom:10px;">{label}</div>
            <div style="display:inline-block; background:{info['color']}22; color:{info['color']}; padding:4px 12px; border-radius:8px; font-size:0.7rem; font-weight:900; border:1px solid {info['color']}44; margin-bottom:15px;">
                {info['status'].upper()}
            </div>
            <p style="color:{TEXT_DIM}; font-size:0.85rem; line-height:1.4;">{info['desc']}</p>
            <div style="display:flex; justify-content:space-between; margin-top:25px; align-items:center;">
                <span style="color:{TEXT_DIM}; font-size:0.8rem;">Confidence</span>
                <span style="color:{ACCENT}; font-weight:900; font-size:1.5rem;">{conf:.1%}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="eyebrow">Inventory Count</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="bento-card">', unsafe_allow_html=True)
    if not st.session_state.inventory:
        st.markdown(f"<span style='color:{TEXT_DIM};'>No specimens detected yet.</span>", unsafe_allow_html=True)
    for species, count in st.session_state.inventory.items():
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid {BORDER}; padding: 5px 0;">
                <span style="color:{TEXT}; font-weight:600;">{species}</span>
                <span style="color:{ACCENT}; font-weight:800;">{count}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Configuration Settings Section ──
    st.markdown('<p class="eyebrow">System Configuration</p>', unsafe_allow_html=True)
    with st.expander("Adjust Parameters", expanded=True):
        target_email = st.text_input("Alert Recipient", value="agiridhar41@gmail.com")
        threshold = st.slider("Alert Threshold (Pop.)", 1, 50, 5)
        if st.button("Reset All Data", use_container_width=True):
            st.session_state.inventory = {}
            st.session_state.emails_sent = []
            st.rerun()

# ── Reference Database Grid ───────────────────────────────
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
                    <div class="bento-card" style="border-left: 4px solid {data['color']}; min-height:160px;">
                        <div style="color:{data['color']}; font-size:0.6rem; font-weight:900; margin-bottom:5px;">{data['status'].upper()}</div>
                        <div style="font-family:'Playfair Display'; font-size:1.5rem; color:{TEXT}; margin-bottom:8px;">{name}</div>
                        <div style="color:{TEXT_DIM}; font-size:0.8rem; line-height:1.4;">{data['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
