import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
from ultralytics import YOLO
import PIL.Image
import numpy as np
import time
import av
import threading
import os

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Communify | Nature Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Theme State ───────────────────────────────────────────
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True
dark = st.session_state.dark_mode

# ── Communify Design Tokens ───────────────────────────────
if dark:
    BG, CARD, TEXT = "#1C1B18", "#2A2824", "#F5F3F0"
    TEXT_DIM, ACCENT, BORDER = "#B8A584", "#D4A574", "#4A4844"
else:
    BG, CARD, TEXT = "#FAF9F6", "#FFFFFF", "#2C2416"
    TEXT_DIM, ACCENT, BORDER = "#6B5D47", "#8B6F47", "#E8E0D6"

# ── CSS Framework ─────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@600;700&display=swap');
.main, [data-testid="stAppViewContainer"] {{ background-color: {BG} !important; font-family: 'Inter', sans-serif !important; }}
.nav-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 0; margin-bottom: 2rem; border-bottom: 1px solid {BORDER}; }}
.bento-card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 28px; padding: 28px; box-shadow: 0 12px 40px rgba(0,0,0,0.04); margin-bottom: 24px; }}
.hero-title {{ font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 700; color: {TEXT}; line-height: 1.1; margin-bottom: 0.75rem; }}
.eyebrow {{ text-transform: uppercase; letter-spacing: 3px; font-size: 0.7rem; font-weight: 700; color: {ACCENT}; margin-bottom: 12px; }}
.metric-val {{ font-family: 'Playfair Display', serif; font-size: 2.5rem; color: {TEXT}; font-weight: 600; }}
div.stButton > button {{ background-color: {ACCENT} !important; color: white !important; border-radius: 14px !important; width: 100%; border: none !important; font-weight: 600 !important; }}
#MainMenu, footer, [data-testid="stHeader"] {{display: none;}}
</style>
""", unsafe_allow_html=True)

# ── Model Loading ─────────────────────────────────────────
@st.cache_resource
def load_classification_model():
    return YOLO('exp-2.pt')

model = load_classification_model()

def get_classification(img_input):
    results = model.predict(img_input, verbose=False)
    if results and results[0].probs:
        top_idx = results[0].probs.top1
        conf = results[0].probs.top1conf.item()
        label = model.names[top_idx]
        return label, conf
    return "No Subject", 0.0

# ── UI Header ─────────────────────────────────────────────
st.markdown(f"""
    <div class="nav-bar">
        <div style="font-family:'Playfair Display'; font-size: 1.6rem; font-weight:700; color:{TEXT}">
            <span style="color:{ACCENT}">♥</span> Communify
        </div>
        <div style="color:{TEXT_DIM}; font-size: 0.75rem; font-weight:700; letter-spacing:2px">INTELLIGENCE HUB</div>
    </div>
""", unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────
col_feed, col_data = st.columns([1.8, 1])

with col_feed:
    st.markdown(f'<p class="eyebrow">Input Source</p>', unsafe_allow_html=True)
    src_tabs = st.tabs(["🖼 Static Analysis", "📷 Live Stream"])
    
    with src_tabs[0]:
        sub1, sub2 = st.columns(2)
        with sub1:
            if st.button("Load Demo Image"):
                # Updated filename to demo_image.jpg
                if os.path.exists("demo_image.jpg"):
                    st.session_state.active_img = PIL.Image.open("demo_image.jpg")
                else:
                    st.error("File 'demo_image.jpg' not found in root directory.")
        
        with sub2:
            uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
            if uploaded_file:
                st.session_state.active_img = PIL.Image.open(uploaded_file)

        if "active_img" in st.session_state:
            st.image(st.session_state.active_img, use_container_width=True)
            if st.button("Run Intelligence Engine"):
                label, conf = get_classification(st.session_state.active_img)
                st.session_state.analysis_result = (label, conf)
    
    with src_tabs[1]:
        webrtc_streamer(
            key="communify-live",
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
        )

with col_data:
    st.markdown(f'<p class="eyebrow">Classification Result</p>', unsafe_allow_html=True)
    res_label, res_conf = st.session_state.get("analysis_result", ("Awaiting Input", 0.0))
    
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Identified Category</p>
            <div class="metric-val">{res_label.replace('_', ' ').title()}</div>
            <div style="margin-top: 24px; background: {BORDER}; height: 8px; border-radius: 10px; overflow: hidden;">
                <div style="background: {ACCENT}; width: {res_conf*100}%; height: 100%; border-radius: 10px;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.85rem; margin-top: 12px; font-weight: 600;">
                Confidence: {res_conf:.2%}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="bento-card" style="background: {ACCENT}; border: none;">
            <p class="eyebrow" style="color: {BG};">Communify Hub</p>
            <p style="color: {BG}; font-size: 0.9rem; margin-bottom: 20px;">
                Identified nature resource. Connect with Pittsburgh conservation groups.
            </p>
            <div style="background: {BG}; color: {ACCENT}; padding: 12px; border-radius: 12px; text-align: center; font-weight: 700; font-size: 0.8rem;">
                VIEW LOCAL ORGANIZATIONS
            </div>
        </div>
    """, unsafe_allow_html=True)
