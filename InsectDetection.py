import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import opencv-headless
from ultralytics import YOLO
import PIL.Image
import os

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Intelligence | YOLO11",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Natural Earth & Forest Palette ────────────────────────
BG       = "#F0F4EF"  # Soft Sage Mist
CARD     = "#FFFFFF"  # Clean White
TEXT     = "#1E352F"  # Deep Spruce
TEXT_DIM = "#4A6741"  # Moss Green
ACCENT   = "#2D5A27"  # Forest Fern
BORDER   = "#D8E2DC"  # Pebble Grey

# ── Custom CSS ────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');

.main, [data-testid="stAppViewContainer"] {{ 
    background-color: {BG} !important; 
    font-family: 'Inter', sans-serif !important; 
}}

.bento-card {{ 
    background: {CARD}; 
    border: 1px solid {BORDER}; 
    border-radius: 24px; 
    padding: 24px; 
    box-shadow: 0 10px 30px rgba(30,53,47,0.05); 
    margin-bottom: 20px; 
}}

.hero-title {{ 
    font-family: 'Playfair Display', serif; 
    font-size: 2.5rem; 
    color: {TEXT}; 
    margin-bottom: 0.5rem; 
}}

.eyebrow {{ 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-size: 0.7rem; 
    font-weight: 700; 
    color: {ACCENT}; 
    margin-bottom: 8px; 
}}

/* Styled Buttons */
div.stButton > button {{ 
    background-color: {ACCENT} !important; 
    color: white !important; 
    border-radius: 12px !important; 
    border: none !important; 
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
}}

/* Remove Streamlit Header/Footer */
#MainMenu, footer, [data-testid="stHeader"] {{display: none;}}
</style>
""", unsafe_allow_html=True)

# ── Model Loading (YOLO11s-cls) ───────────────────────────
@st.cache_resource
def load_insect_model():
    # Loading your uploaded exp.pt (YOLO11)
    return YOLO('exp.pt')

model = load_insect_model()

def classify_image(img):
    results = model.predict(img, verbose=False)
    if results and results[0].probs:
        idx = results[0].probs.top1
        conf = results[0].probs.top1conf.item()
        label = model.names[idx]
        return label, conf
    return "Unknown Specimen", 0.0

# ── Navigation ────────────────────────────────────────────
st.markdown(f"""
    <div style="padding: 1.5rem 0; border-bottom: 1px solid {BORDER}; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-family:'Playfair Display'; font-size: 1.5rem; font-weight:700; color:{TEXT}">
            🌿 Insect Detection <span style="font-weight:400; font-size:0.9rem; color:{TEXT_DIM}">v1.1</span>
        </div>
        <div style="font-size: 0.7rem; font-weight: 700; color:{TEXT_DIM}; letter-spacing:1px;">POWERED BY YOLO11s</div>
    </div>
""", unsafe_allow_html=True)

# ── Main UI ───────────────────────────────────────────────
col_input, col_results = st.columns([1.6, 1])

with col_input:
    st.markdown('<p class="eyebrow">Data Acquisition</p>', unsafe_allow_html=True)
    tabs = st.tabs(["🖼 Static Capture", "📷 Real-time Stream"])
    
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load Demo Specimen"):
                if os.path.exists("demo_image.jpg"):
                    st.session_state.active_img = PIL.Image.open("demo_image.jpg")
                else:
                    st.error("demo_image.jpg not found.")
        
        with c2:
            up = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if up:
                st.session_state.active_img = PIL.Image.open(up)

        if "active_img" in st.session_state:
            st.image(st.session_state.active_img, use_container_width=True)
            if st.button("Run Classification Engine"):
                label, conf = classify_image(st.session_state.active_img)
                st.session_state.insect_res = (label, conf)
    
    with tabs[1]:
        webrtc_streamer(
            key="insect-stream",
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
        )

with col_results:
    st.markdown('<p class="eyebrow">Taxonomy Analysis</p>', unsafe_allow_html=True)
    
    label, conf = st.session_state.get("insect_res", ("Awaiting Input", 0.0))
    
    # Analysis Bento Card
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Top Prediction</p>
            <div style="font-family:'Playfair Display'; font-size: 2rem; color:{TEXT}; margin-bottom: 15px;">
                {label.replace('_', ' ').title()}
            </div>
            <div style="background: {BORDER}; height: 6px; border-radius: 10px; overflow: hidden;">
                <div style="background: {ACCENT}; width: {conf*100}%; height: 100%;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; margin-top: 10px; font-weight: 600;">
                Confidence Score: {conf:.2%}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Info Card
    st.markdown(f"""
        <div class="bento-card" style="background: {TEXT}; border: none;">
            <p class="eyebrow" style="color: {BORDER};">Engine Specs</p>
            <p style="color: white; font-size: 0.85rem; opacity: 0.8;">
                This deployment utilizes a YOLO11-Small classification head optimized for mobile-responsive environments.
            </p>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid {TEXT_DIM}; font-size: 0.7rem; color: {BORDER};">
                ARCH: YOLO11s-cls<br>
                WEIGHTS: exp.pt<br>
                INPUT: 224x224 (Internal)
            </div>
        </div>
    """, unsafe_allow_html=True)
