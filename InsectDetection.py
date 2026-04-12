import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
from ultralytics import YOLO
import PIL.Image
import os

# ── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="Insect Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme Toggle (Sidebar) ────────────────────────────────
with st.sidebar:
    st.markdown("### UI Settings")
    dark_mode = st.toggle("Dark Mode", value=True)
    st.divider()
    st.markdown("🔍 **Model:** YOLO11s-cls")
    st.markdown("📂 **Weights:** `exp.pt`平衡")

# ── Dynamic Color Palette ─────────────────────────────────
if dark_mode:
    BG       = "#121412"  # Deep Charcoal Green
    CARD     = "#1C1F1C"  # Dark Moss Card
    TEXT     = "#E0E4E0"  # Off-white Sage
    TEXT_DIM = "#8AA38D"  # Muted Leaf
    ACCENT   = "#4CAF50"  # Vibrant Nature Green
    BORDER   = "#2D332D"  # Dark Border
else:
    BG       = "#F4F7F4"  # Light Mint Cream
    CARD     = "#FFFFFF"  # White
    TEXT     = "#1B2E1B"  # Deep Forest
    TEXT_DIM = "#556B2F"  # Olive
    ACCENT   = "#2E8B57"  # Sea Green
    BORDER   = "#D1DBCC"  # Pale Sage

# ── CSS Overrides (Removing Red & Adding Theme) ───────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap');

    /* Remove Streamlit Red Accents */
    [data-testid="stHeader"], header, footer {{ visibility: hidden; display: none; }}
    .stAppViewDecoration {{ background-image: none !important; background-color: {BG} !important; }}
    
    /* Base Theme */
    .main, [data-testid="stAppViewContainer"] {{ 
        background-color: {BG} !important; 
        font-family: 'Inter', sans-serif !important; 
    }}

    /* Bento Cards */
    .bento-card {{ 
        background: {CARD}; 
        border: 1px solid {BORDER}; 
        border-radius: 24px; 
        padding: 24px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        color: {TEXT};
    }}

    .eyebrow {{ 
        text-transform: uppercase; letter-spacing: 2px; 
        font-size: 0.7rem; font-weight: 700; color: {ACCENT}; 
        margin-bottom: 8px; 
    }}

    /* UI Components */
    div.stButton > button {{ 
        background-color: {ACCENT} !important; 
        color: white !important; 
        border-radius: 12px !important; 
        border: none !important; 
        width: 100%;
        font-weight: 600 !important;
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{ color: {TEXT_DIM}; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {ACCENT}; }}
</style>
""", unsafe_allow_html=True)

# ── Model Loading ─────────────────────────────────────────
@st.cache_resource
def load_insect_model():
    return YOLO('exp.pt')

model = load_insect_model()

def classify(img):
    results = model.predict(img, verbose=False)
    if results and results[0].probs:
        idx = results[0].probs.top1
        conf = results[0].probs.top1conf.item()
        return model.names[idx], conf
    return "Unknown", 0.0

# ── Main UI ───────────────────────────────────────────────
st.markdown(f'<h1 style="font-family:Playfair Display; color:{TEXT}; margin-bottom:2rem;">Insect Detection</h1>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<p class="eyebrow">Input Feed</p>', unsafe_allow_html=True)
    tabs = st.tabs(["🖼 Upload / Demo", "📷 Live Stream"])
    
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load Demo Specimen"):
                if os.path.exists("demo_image.jpg"):
                    st.session_state.active_img = PIL.Image.open("demo_image.jpg")
                else:
                    st.error("demo_image.jpg missing.")
        with c2:
            up = st.file_uploader("Upload", type=["jpg","png"], label_visibility="collapsed")
            if up: st.session_state.active_img = PIL.Image.open(up)

        if "active_img" in st.session_state:
            st.image(st.session_state.active_img, use_container_width=True)
            if st.button("Analyze Specimen"):
                label, conf = classify(st.session_state.active_img)
                st.session_state.insect_res = (label, conf)
    
    with tabs[1]:
        webrtc_streamer(
            key="live-insect",
            rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
            media_stream_constraints={"video": True, "audio": False},
        )

with col_right:
    st.markdown('<p class="eyebrow">Taxonomy Result</p>', unsafe_allow_html=True)
    label, conf = st.session_state.get("insect_res", ("Awaiting Data", 0.0))
    
    st.markdown(f"""
        <div class="bento-card">
            <p class="eyebrow">Identification</p>
            <div style="font-family:'Playfair Display'; font-size: 2.2rem; color:{TEXT};">
                {label.replace('_', ' ').title()}
            </div>
            <div style="background: {BORDER}; height: 8px; border-radius: 10px; margin-top: 1.5rem; overflow: hidden;">
                <div style="background: {ACCENT}; width: {conf*100}%; height: 100%;"></div>
            </div>
            <p style="color: {TEXT_DIM}; font-size: 0.8rem; margin-top: 10px; font-weight: 600;">
                Confidence: {conf:.2%}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="bento-card" style="background: {ACCENT}; border: none;">
            <p class="eyebrow" style="color: rgba(255,255,255,0.7);">System Status</p>
            <p style="color: white; font-size: 0.9rem;">
                Neural engine active. YOLO11 architecture optimized for low-latency classification.
            </p>
        </div>
    """, unsafe_allow_html=True)
