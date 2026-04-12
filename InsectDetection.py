import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
from ultralytics import YOLO
import PIL.Image
import os

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Detection Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Natural Color Palette ────────────────────────────────
# Using Forest Green, Moss, and Earth tones
BG       = "#F4F7F4"  # Very light mint/cream
CARD     = "#FFFFFF"  # White
TEXT     = "#1B2E1B"  # Deep Forest Green
TEXT_DIM = "#556B2F"  # Dark Olive Green
ACCENT   = "#2E8B57"  # Sea Green
BORDER   = "#D1DBCC"  # Pale Sage

# ── Custom CSS ────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');

.main, [data-testid="stAppViewContainer"] {{ 
    background-color: {BG} !important; 
    font-family: 'Inter', sans-serif !important; 
}}

/* Bento Card Style */
.bento-card {{ 
    background: {CARD}; 
    border: 1px solid {BORDER}; 
    border-radius: 24px; 
    padding: 24px; 
    box-shadow: 0 8px 32px rgba(0,0,0,0.03); 
    margin-bottom: 20px; 
}}

.hero-title {{ 
    font-family: 'Playfair Display', serif; 
    font-size: 2.8rem; 
    color: {TEXT}; 
    margin-bottom: 0.5rem; 
}}

.eyebrow {{ 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-size: 0.75rem; 
    font-weight: 700; 
    color: {ACCENT}; 
    margin-bottom: 10px; 
}}

.metric-val {{ 
    font-family: 'Playfair Display', serif; 
    font-size: 2.2rem; 
    color: {TEXT}; 
}}

/* Button Customization */
div.stButton > button {{ 
    background-color: {ACCENT} !important; 
    color: white !important; 
    border-radius: 12px !important; 
    border: none !important; 
    font-weight: 600 !important;
    transition: 0.3s;
}}

div.stButton > button:hover {{
    background-color: {TEXT_DIM} !important;
    transform: translateY(-2px);
}}

#MainMenu, footer, [data-testid="stHeader"] {{display: none;}}
</style>
""", unsafe_allow_html=True)

# ── Model Loading ─────────────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO('exp-2.pt')

model = load_model()

def run_prediction(img):
    results = model.predict(img, verbose=False)
    if results and results[0].probs:
        idx = results[0].probs.top1
        conf = results[0].probs.top1conf.item()
        return model.names[idx], conf
    return "No Data", 0.0

# ── Header ────────────────────────────────────────────────
st.markdown(f"""
    <div style="padding: 1rem 0; border-bottom: 1px solid {BORDER}; margin-bottom: 2rem; display: flex; align-items: center; gap: 10px;">
        <div style="background: {ACCENT}; width: 12px; height: 12px; border-radius: 50%;"></div>
        <div style="font-family:'Playfair Display'; font-size: 1.4rem; font-weight:700; color:{TEXT}">
            Insect Detection
        </div>
    </div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<p class="eyebrow">Visual Data Feed</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🖼 Static Analysis", "📷 Live Stream"])
    
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load Demo Insect"):
                if os.path.exists("demo_image.jpg"):
                    st.session_state.active_img = PIL.Image.open("demo_image.jpg")
                else:
                    st.error("demo_image.jpg not found.")
        
        with c2:
            up = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if up:
                st.session_state.active_img = PIL.Image.open(up)

        if "active_img" in st.session_state:
            st.markdown(f'<div style="border: 4px solid {BORDER}; border-radius: 20px; overflow: hidden;">', unsafe_allow_html=True)
            st.image(st.session_state.active_img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Classify Specimen"):
                label, conf = run_prediction(st.session_state.active_img)
                st.session_state.res = (label, conf)
    
    with tabs[1]:
        webrtc_streamer(
            key="insect-cam",
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
        )
        st.caption("Whole-image classification active for video stream.")

with col_right:
    st.markdown('<p class="eyebrow">Analysis Dashboard</p>', unsafe_allow_html=True)
    
    label, conf = st.session_state.get("res", ("Awaiting Input", 0.0))
    
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Primary Classification</p>
            <div class="metric-val">{label.replace('_', ' ').title()}</div>
            <div style="background: {BORDER}; height: 8px; border-radius: 10px; margin-top: 20px; overflow: hidden;">
                <div style="background: {ACCENT}; width: {conf*100}%; height: 100%;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.85rem; margin-top: 10px; font-weight: 600;">
                Confidence Index: {conf:.2%}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="bento-card" style="background: {TEXT}; color: white; border: none;">
            <p class="eyebrow" style="color: {BORDER};">Taxonomy Info</p>
            <p style="font-size: 0.9rem; opacity: 0.9; line-height: 1.5;">
                This engine uses a YOLOv8-Cls architecture trained specifically for regional insect identification.
            </p>
            <hr style="border-color: {TEXT_DIM}; margin: 15px 0;">
            <div style="font-size: 0.75rem; color: {BORDER};">
                MODEL: exp-2.pt<br>
                FORMAT: CLASSIFICATION
            </div>
        </div>
    """, unsafe_allow_html=True)
