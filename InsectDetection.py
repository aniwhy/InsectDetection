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

# ── Theme State & Toggle ──────────────────────────────────
t_col1, t_col2 = st.columns([8, 1.5])
with t_col2:
    # Adding a label here so we can target it with CSS
    dark_mode = st.toggle("Light/Dark Mode", value=True)

# ── Dynamic Color Palette ─────────────────────────────────
if dark_mode:
    BG, CARD, TEXT = "#121412", "#1C1F1C", "#E0E4E0"
    TEXT_DIM, ACCENT, BORDER = "#8AA38D", "#4CAF50", "#2D332D"
else:
    BG, CARD, TEXT = "#F4F7F4", "#FFFFFF", "#1B2E1B"
    TEXT_DIM, ACCENT, BORDER = "#556B2F", "#2E8B57", "#D1DBCC"

# ── CSS Overrides (Deep Browser Targeting) ────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');
    
    /* Global Reset */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-image: none !important; background-color: {BG} !important; }}
    .main, [data-testid="stAppViewContainer"] {{ background-color: {BG} !important; font-family: 'Inter', sans-serif !important; }}

    /* ── FIXING THE INVISIBLE TEXT ── */
    /* This targets the labels for toggles and uploaders directly */
    .stText, .stMarkdown p, label, .stToggle label p {{
        color: {TEXT} !important;
        font-weight: 600 !important;
    }}

    /* ── UPLOAD BOX FIX ── */
    [data-testid="stFileUploader"] {{
        background-color: {CARD} !important;
        border: 2px dashed {ACCENT} !important;
        border-radius: 15px !important;
    }}
    
    /* Force the 'Browse files' button to stay dark/visible */
    [data-testid="stFileUploader"] button {{
        background-color: {ACCENT} !important;
        color: white !important;
    }}

    /* Target the 'Drag and drop' small text that ghosts out */
    [data-testid="stFileUploadDropzone"] div div span {{
        color: {TEXT} !important;
    }}

    /* ── TOGGLE FIX ── */
    /* The track */
    div[role="switch"] {{
        background-color: {BORDER} !important;
    }}
    div[role="switch"][aria-checked="true"] {{
        background-color: {BORDER} !important;
    }}
    /* The moving circle (handle) */
    div[role="switch"] > div {{
        background-color: {ACCENT} !important;
    }}

    /* ── UI ELEMENTS ── */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.05); 
        margin-bottom: 20px; 
    }}

    .eyebrow {{ 
        text-transform: uppercase; letter-spacing: 2px; 
        font-size: 0.7rem; font-weight: 700; color: {ACCENT} !important; 
        margin-bottom: 8px; 
    }}

    div.stButton > button {{ 
        background-color: {ACCENT} !important; 
        color: white !important; 
        border-radius: 12px !important; 
    }}
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
        
        # High threshold to prevent misidentifying humans
        if conf < 0.55:
            return "No Specimen Detected", conf
        return label, conf
    return "Scanning...", 0.0

# ── Main UI ───────────────────────────────────────────────
st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin-top:-40px;">Insect Detection</h1>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<p class="eyebrow">Data Intake</p>', unsafe_allow_html=True)
    tabs = st.tabs(["Camera Control", "Manual Upload"])
    
    with tabs[0]:
        cam_image = st.camera_input("Snapshot", label_visibility="collapsed")
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        auto_poll = st.toggle("Enable Auto-Analysis Loop", value=False)
        
        if cam_image:
            img = PIL.Image.open(cam_image)
            label, conf = classify(img)
            st.session_state.insect_res = (label, conf)
            
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

with col_right:
    st.markdown('<p class="eyebrow">Result Engine</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    display_label = label.replace('_', ' ').title()
    
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Identification</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">
                {display_label}
            </div>
            <div style="background: {BORDER}; height: 8px; border-radius: 10px; margin-top: 1.5rem; overflow: hidden;">
                <div style="background: {ACCENT}; width: {conf*100}%; height: 100%;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; margin-top: 10px; font-weight: 600;">
                Confidence: {conf:.2%}
            </p>
        </div>
    """, unsafe_allow_html=True)

# ── Footer Project Details ────────────────────────────────
st.markdown(f"""
    <div style="margin-top: 4rem; padding: 2rem 0; border-top: 1px solid {BORDER}; text-align: center;">
        <p style="color: {TEXT_DIM}; font-size: 0.8rem; letter-spacing: 1px; margin: 0;">
            TSA 2026 | SEVEN SPRINGS, PA
        </p>
        <p style="color: {TEXT}; font-weight: 600; font-size: 0.9rem; margin-top: 5px;">
            TEAM ID: 2043-901
        </p>
        <p style="color: {TEXT_DIM}; font-size: 0.75rem;">
            IDs: 2043-022, 2043-084, 2043-085
        </p>
    </div>
""", unsafe_allow_html=True)
