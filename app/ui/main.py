"""
FIBO Continuity Director - Canva-Inspired Design
Built for FIBO Hackathon 2024 | Powered by Bria FIBO API
"""
import streamlit as st
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Ensure root path is in sys.path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Imports
import base64
try:
    from app.core import planner, engine, validator
    from app.core import director_agent, story_arc, script_parser, style_dna
    from app.utils import helpers as utils
    from app.models import config
    from app.models.schemas import ProjectPlan
except ImportError:
    from ..core import planner, engine, validator
    from ..core import director_agent, story_arc, script_parser, style_dna
    from ..utils import helpers as utils
    from ..models import config
    from ..models.schemas import ProjectPlan

logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="MindLens", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CANVA-INSPIRED CSS
# ============================================================================
st.markdown("""
<style>
    /* Import elegant script font */
    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* ===== COLOR PALETTE =====
    Primary Purple:  #8B3DFF (Canva violet)
    Light Purple:    #E5D4FF
    Dark Purple:     #5B1FB8
    Background:      #F0F0F0 (light gray)
    Card White:      #FFFFFF
    Text Dark:       #1A1A1A
    Text Gray:       #6B7280
    Success Green:   #00C853
    ===== */
    
    /* ===== RESET ===== */
    #MainMenu, footer, header {visibility: hidden; height: 0 !important;}
    
    /* Kill ALL top spacing */
    .stApp, .main, .block-container, 
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stAppViewContainer"] > section,
    [data-testid="stVerticalBlock"],
    .main > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit's top bar completely */
    .stApp > header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display: none !important;
        height: 0 !important;
    }
    
    /* Force header-bar to top */
    .header-bar {
        position: relative;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
    }
    
    /* ===== MAIN BACKGROUND ===== */
    .stApp {
        background: 
            /* Frosted overlay - lighter */
            linear-gradient(180deg, 
                rgba(245, 240, 255, 0.6) 0%,
                rgba(250, 248, 255, 0.5) 50%,
                rgba(245, 240, 255, 0.6) 100%
            ),
            /* Bokeh circles effect - more visible */
            radial-gradient(circle at 10% 15%, rgba(139, 61, 255, 0.35) 0%, transparent 20%),
            radial-gradient(circle at 90% 20%, rgba(183, 148, 246, 0.4) 0%, transparent 18%),
            radial-gradient(circle at 75% 65%, rgba(139, 61, 255, 0.3) 0%, transparent 25%),
            radial-gradient(circle at 20% 75%, rgba(183, 148, 246, 0.35) 0%, transparent 22%),
            radial-gradient(circle at 50% 5%, rgba(139, 61, 255, 0.25) 0%, transparent 30%),
            radial-gradient(circle at 95% 80%, rgba(183, 148, 246, 0.3) 0%, transparent 15%),
            radial-gradient(circle at 5% 50%, rgba(139, 61, 255, 0.2) 0%, transparent 20%),
            radial-gradient(circle at 60% 90%, rgba(183, 148, 246, 0.25) 0%, transparent 18%),
            /* Base - very light */
            linear-gradient(135deg, #F8F5FF 0%, #FFFFFF 50%, #F8F5FF 100%);
        min-height: 100vh;
        background-attachment: fixed;
    }
    
    /* ===== FORCE LIGHT THEME ON ALL CONTAINERS ===== */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    .stMarkdown,
    .stAlert,
    .element-container,
    div[data-baseweb] {
        background-color: transparent !important;
    }
    
    /* Remove white boxes from columns and padding areas */
    [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlock"],
    [data-testid="stColumn"],
    .stColumn,
    .stColumn > div,
    .stColumn > div > div,
    [data-testid="stVerticalBlock"] > div,
    [data-testid="stVerticalBlock"] > div > div,
    [data-testid="stHorizontalBlock"] > div,
    [data-testid="stHorizontalBlock"] > div > div {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Ensure all text is dark by default */
    .stApp p, .stApp span, .stApp div, .stApp label, .stApp small {
        color: #1A1A1A !important;
    }
    
    /* ===== TYPOGRAPHY ===== */
    * {
        font-family: 'Poppins', 'Segoe UI', -apple-system, sans-serif;
    }
    
    /* ===== GLOBAL LABELS ===== */
    .stApp label,
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stSlider label,
    .stFileUploader label,
    .stCheckbox label span,
    .stRadio label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stMarkdownContainer"] label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #8B3DFF !important;
        margin-bottom: 8px !important;
    }
    
    /* ===== SECTION TITLES (Project Setup, Character, etc.) ===== */
    .section-title {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #1A1A1A !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
        font-family: 'Poppins', sans-serif;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ===== HEADER ===== */
    .header-bar {
        background: transparent;
        padding: 15px 40px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: none;
        margin-bottom: 20px;
        margin-top: -1rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .logo-icon {
        font-size: 2.2rem;
    }
    
    .logo-icon-svg {
        width: 45px;
        height: 45px;
    }
    
    .logo-text {
        font-family: 'Great Vibes', cursive;
        font-size: 5rem;
        font-weight: 600;
        font-style: italic;
        color: #8B3DFF;
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(139, 61, 255, 0.2);
        transform: skewX(-5deg);
    }
    
    .logo-wrapper {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    
    .logo-flourish {
        width: 280px;
        height: 30px;
        margin-top: -25px;
        margin-left: 0;
    }
    
    .nav-links {
        display: flex;
        gap: 25px;
    }
    
    .nav-link {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: color 0.2s;
    }
    
    .nav-link:hover {
        color: #FFFFFF;
    }
    
    .pro-btn {
        background: #FFFFFF;
        color: #8B3DFF;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .pro-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
    }
    
    /* ===== CARDS ===== */
    .card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(139, 61, 255, 0.12);
        margin-bottom: 16px;
        border-left: 4px solid #8B3DFF;
    }
    
    /* Hide empty card divs from split st.markdown calls */
    .card:empty,
    .stMarkdown .card:only-child {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
        height: 0 !important;
        box-shadow: none !important;
    }
    
    /* Hide opening/closing card tags that appear as separate elements */
    p:has(> .card:empty),
    div.stMarkdown:has(> .card:empty) {
        display: none !important;
    }
    
    /* Hide empty Streamlit containers that appear as white boxes */
    .stMarkdown:empty,
    .element-container:empty,
    [data-testid="stVerticalBlock"] > div:empty,
    .stColumn > div:empty {
        display: none !important;
    }
    
    /* Ensure streamlit's extra wrappers are transparent */
    [data-testid="stVerticalBlock"] > div > div:not(.card),
    .stColumn > div > div:not(.card) {
        background: transparent !important;
        box-shadow: none !important;
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #8B3DFF 0%, #5B1FB8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(139, 61, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(139, 61, 255, 0.4) !important;
    }
    
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #FFFFFF !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 10px !important;
        color: #1A1A1A !important;
        padding: 14px !important;
        font-size: 1rem !important;
        transition: border-color 0.2s !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #8B3DFF !important;
        box-shadow: 0 0 0 3px rgba(139, 61, 255, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #9CA3AF !important;
    }
    
    /* ===== SLIDERS ===== */
    .stSlider [role="slider"] {
        background: #8B3DFF !important;
    }
    
    .stSlider > div > div > div > div {
        background: #E5D4FF !important;
    }
    
    .stSlider label {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    
    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox label {
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }
    
    /* Fix selectbox text and value visibility */
    .stSelectbox [data-baseweb="select"] {
        background: #FFFFFF !important;
    }
    
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #1A1A1A !important;
    }
    
    /* Dropdown menu styling */
    [data-baseweb="popover"] {
        background: #FFFFFF !important;
    }
    
    [data-baseweb="menu"] {
        background: #FFFFFF !important;
    }
    
    [data-baseweb="menu"] li {
        color: #1A1A1A !important;
        background: #FFFFFF !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background: #E5D4FF !important;
    }
    
    /* ===== CHECKBOXES ===== */
    .stCheckbox label {
        color: #1A1A1A !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox label span {
        color: #1A1A1A !important;
    }
    
    /* ===== RADIO ===== */
    .stRadio label {
        color: #1A1A1A !important;
        font-weight: 500 !important;
    }
    
    .stRadio label span,
    .stRadio [role="radiogroup"] label {
        color: #1A1A1A !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader {
        background: #FFFFFF !important;
        border: 2px dashed #8B3DFF !important;
        border-radius: 10px !important;
    }
    
    .stFileUploader label {
        color: #1A1A1A !important;
    }
    
    /* Fix file uploader inner container */
    .stFileUploader > div,
    .stFileUploader section,
    .stFileUploader [data-testid="stFileUploader"],
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background: #F8F5FF !important;
        border-radius: 10px !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #5B1FB8 !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] div,
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] span,
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: #6B7280 !important;
    }
    
    .stFileUploader button {
        background: #8B3DFF !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    /* Fix all text inside file uploader */
    [data-testid="stFileUploader"] * {
        color: #1A1A1A !important;
    }
    
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button * {
        color: white !important;
    }
    
    /* ===== TAGS ===== */
    .tag {
        display: inline-block;
        background: #E5D4FF;
        color: #5B1FB8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
    }
    
    .tag-pro {
        background: linear-gradient(135deg, #8B3DFF 0%, #5B1FB8 100%);
        color: white;
    }
    
    /* ===== SECTION TITLE ===== */
    .section-title {
        font-size: 1rem;
        font-weight: 800;
        color: #5B1FB8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
    }
    
    /* ===== FOOTER ===== */
    .footer-bar {
        background: transparent;
        padding: 25px 40px;
        text-align: center;
        margin-top: 40px;
    }
    
    .footer-text {
        color: #5B1FB8;
        font-size: 0.85rem;
    }
    
    .footer-link {
        color: #8B3DFF;
        font-weight: 600;
        text-decoration: none;
    }
    
    .footer-link:hover {
        text-decoration: underline;
        color: #5B1FB8;
    }
    
    /* ===== WELCOME SCREEN ===== */
    .welcome-container {
        text-align: center;
        padding: 80px 40px;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1A1A1A;
        margin-bottom: 16px;
    }
    
    .welcome-highlight {
        color: #8B3DFF;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #6B7280;
        max-width: 500px;
        margin: 0 auto 30px;
        line-height: 1.6;
    }
    
    /* ===== DIVIDERS ===== */
    hr {
        border: none;
        height: 1px;
        background: #E5E7EB;
        margin: 20px 0;
    }
    
    /* ===== DOWNLOAD BUTTONS ===== */
    .stDownloadButton > button {
        background: #FFFFFF !important;
        border: 2px solid #8B3DFF !important;
        color: #8B3DFF !important;
        box-shadow: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: #8B3DFF !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if "project_plan" not in st.session_state:
    st.session_state["project_plan"] = None
if "outputs" not in st.session_state:
    st.session_state["outputs"] = []
if "grid_path" not in st.session_state:
    st.session_state["grid_path"] = None
if "video_path" not in st.session_state:
    st.session_state["video_path"] = None
if "hdr_enabled" not in st.session_state:
    st.session_state["hdr_enabled"] = True
if "bit_depth" not in st.session_state:
    st.session_state["bit_depth"] = "16-bit"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def run_generation(plan: ProjectPlan, reference_image_path: str = None):
    """Run sequence generation."""
    progress = st.progress(0)
    status = st.empty()
    
    def on_progress(current, total, shot_id):
        progress.progress((current + 1) / total)
        status.markdown(f"<p style='color:#8B3DFF; text-align:center;'>✨ Creating shot {current + 1}/{total}</p>", unsafe_allow_html=True)
    
    outputs = engine.generate_sequence(plan, progress_callback=on_progress, reference_image_path=reference_image_path)
    outputs = validator.validate_continuity(outputs)
    st.session_state["outputs"] = outputs
    
    if outputs:
        image_paths = [o["image_path"] for o in outputs if o.get("image_path")]
        if image_paths:
            grid_path = os.path.join(config.OUTPUT_DIR, plan.project_id, "storyboard_grid.png")
            utils.create_storyboard_grid(image_paths, grid_path)
            st.session_state["grid_path"] = grid_path
    
    project_dir = os.path.join(config.OUTPUT_DIR, plan.project_id)
    display_name = st.session_state.get("project_name", plan.project_id[:8])
    utils.save_project(project_dir, display_name, plan.dict(), outputs)
    
    progress.empty()
    status.empty()

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="header-bar">
    <div class="logo-section">
        <div class="logo-wrapper">
            <span class="logo-text">MindLens</span>
            <svg class="logo-flourish" viewBox="0 0 280 30" fill="none">
                <!-- Elegant single swoosh curve -->
                <path d="M5 20 C60 25, 100 8, 150 15 S220 25, 265 10" stroke="#8B3DFF" stroke-width="2" stroke-linecap="round" fill="none"/>
                <!-- Small butterfly at the end -->
                <g transform="translate(268, 8)">
                    <path d="M0 0 Q-5 -6, -8 0 Q-5 6, 0 0" fill="#B794F6"/>
                    <path d="M0 0 Q5 -6, 8 0 Q5 6, 0 0" fill="#8B3DFF"/>
                </g>
            </svg>
        </div>
    </div>
    <span class="pro-btn">✨ Pro Features</span>
</div>
""", unsafe_allow_html=True)

# Pages are in sidebar: ✨ Features, 🖼️ Gallery, 📋 Templates

# ============================================================================
# COMPACT DASHBOARD + DEMO (Single Row)
# ============================================================================
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; background: #1a102880; border-radius: 12px; padding: 10px 16px; border: 1px solid #8B3DFF40; margin-bottom: 16px;">
    <div>
        <span style="color: #B794F6; font-weight: 600;">📊 FIBO APIs:</span>
        <span style="background: linear-gradient(135deg, #8B3DFF, #B794F6); padding: 3px 10px; border-radius: 10px; color: #fff; font-size: 0.8rem; margin-left: 8px;">12/12 ✓</span>
        <span style="color: #9CA3AF; font-size: 0.75rem; margin-left: 10px;">Text2Img • Inspire • HDR • BG Removal • GenFill • Eraser • Expand • Enhance</span>
    </div>
</div>
""", unsafe_allow_html=True)

demo_col1, demo_col2, demo_col3, demo_col4 = st.columns([1.5, 1, 1, 1])
with demo_col1:
    st.markdown("<span style='color: #9CA3AF; font-size: 0.85rem;'>🎬 Quick Demo:</span>", unsafe_allow_html=True)
with demo_col2:
    if st.button("🎭 Drama", key="demo_drama", use_container_width=True):
        st.session_state["brief_input"] = "A tense confrontation in a dimly lit interrogation room. Detective Sarah leans forward."
        st.session_state["char_input"] = "Detective Sarah, a seasoned investigator in her 40s, wearing a dark blazer"
        st.rerun()
with demo_col3:
    if st.button("🌅 Romance", key="demo_romance", use_container_width=True):
        st.session_state["brief_input"] = "Golden hour on a rooftop garden. Two lovers share their first dance."
        st.session_state["char_input"] = "Maya, a young artist with flowing auburn hair, bohemian dress"
        st.rerun()
with demo_col4:
    if st.button("⚔️ Action", key="demo_action", use_container_width=True):
        st.session_state["brief_input"] = "A warrior stands at the edge of a cliff, ancient sword drawn. Lightning cracks."
        st.session_state["char_input"] = "Kai, a battle-scarred warrior with silver hair and weathered armor"
        st.rerun()

# ============================================================================
# 3-COLUMN LAYOUT
# ============================================================================
left_col, center_col, right_col = st.columns([1.2, 2.5, 1.2])

# ============================================================================
# LEFT COLUMN - Project Setup
# ============================================================================
with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Project Setup</div>', unsafe_allow_html=True)
    
    project_name = st.text_input("Project Name", placeholder="My Storyboard")
    
    # Input mode tabs
    input_mode = st.radio("Input Mode", ["✏️ Brief", "📜 Script", "🎬 Story Arc", "✨ Inspire"], horizontal=True, label_visibility="collapsed")
    
    if input_mode == "✏️ Brief":
        # key="brief_input" - session state is set by demo buttons
        brief = st.text_area("Scene Description", height=100, placeholder="Describe your scene...", key="brief_input")
    
    elif input_mode == "📜 Script":
        script_text = st.text_area("Paste Screenplay", height=150, 
            placeholder="INT. COFFEE SHOP - DAY\n\nSARAH enters...", key="script_input")
        if script_text.strip():
            parsed_scenes = script_parser.parse_script(script_text)
            summary = script_parser.get_script_summary(parsed_scenes)
            st.success(f"📍 {summary['total_scenes']} scenes • {len(summary['characters'])} characters")
            brief = f"Screenplay with {summary['total_scenes']} scenes. Locations: {', '.join(summary['locations'][:3])}"
        else:
            brief = ""
    
    elif input_mode == "🎬 Story Arc":
        arc_theme = st.selectbox("Story Theme", ["hero's journey", "rise and fall", "love story", "mystery", "product showcase"])
        arc_brief = st.text_input("Context", placeholder="Add specific details...")
        if arc_theme:
            arc = story_arc.generate_story_arc(arc_theme, 5, arc_brief)
            arc_summary = story_arc.get_arc_summary(arc)
            st.info(f"📊 Setup({arc_summary['structure']['setup']}) → Conflict({arc_summary['structure']['confrontation']}) → Resolution({arc_summary['structure']['resolution']})")
            brief = f"{arc_theme}: {arc_brief}" if arc_brief else arc_theme
        else:
            brief = ""
    
    elif input_mode == "✨ Inspire":
        st.markdown("**Upload an image to generate variations**")
        inspire_image = st.file_uploader("Reference Image", type=["png", "jpg", "jpeg"], key="inspire_img")
        inspire_prompt = st.text_input("Modification (optional)", placeholder="Add sunset lighting, make it dramatic...", key="inspire_prompt")
        
        if inspire_image:
            st.image(inspire_image, caption="Reference Image", width=200)
            brief = inspire_prompt if inspire_prompt.strip() else "Create a variation of this image"
            st.session_state["inspire_mode_image"] = inspire_image
        else:
            brief = ""
            st.caption("Upload an image to use FIBO Inspire Mode")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.selectbox("Mode", ["storyboard", "product"])
    with col2:
        num_shots = st.slider("Shots", 3, 8, 5)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎭 Character</div>', unsafe_allow_html=True)
    
    # key="char_input" - session state is set by demo buttons
    character_description = st.text_area("Main Character", height=60, placeholder="A young woman with curly hair...", key="char_input")
    char_ref_file = st.file_uploader("Reference Image", type=["png", "jpg", "jpeg"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate buttons - both use same sidebar parameters
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        generate_clicked = st.button("✨ Storyboard", type="primary", use_container_width=True)
    with btn_col2:
        single_image_clicked = st.button("🎨 Single Image", use_container_width=True)
    
    # Initialize img2img_clicked to False (handled by Inspire mode now)
    img2img_clicked = False
    
    if not config.FIBO_API_KEY:
        st.error("API Key missing")
    
    # Load projects
    saved_projects = utils.list_saved_projects(config.OUTPUT_DIR)
    if saved_projects:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📂 Recent Projects</div>', unsafe_allow_html=True)
        project_options = ["New"] + [p["project_name"] for p in saved_projects]
        selected = st.selectbox("", project_options, key="load", label_visibility="collapsed")
        
        if selected != "New":
            proj = next((p for p in saved_projects if p["project_name"] == selected), None)
            if proj and st.button("📥 Load", use_container_width=True):
                loaded = utils.load_project(proj["path"])
                if loaded:
                    st.session_state["project_plan"] = loaded["plan"]
                    st.session_state["outputs"] = loaded.get("outputs", [])
                    st.session_state["project_name"] = loaded["project_name"]
                    
                    # Restore grid_path from saved outputs
                    outputs = loaded.get("outputs", [])
                    if outputs:
                        image_paths = [o.get("image_path") for o in outputs if o.get("image_path") and os.path.exists(o.get("image_path", ""))]
                        if image_paths:
                            project_id = loaded["plan"].get("project_id", "loaded")
                            grid_path = os.path.join(config.OUTPUT_DIR, project_id, "storyboard_grid.png")
                            if os.path.exists(grid_path):
                                st.session_state["grid_path"] = grid_path
                            else:
                                # Regenerate grid if missing
                                st.session_state["grid_path"] = utils.create_storyboard_grid(image_paths, grid_path)
                    
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# RIGHT COLUMN - Pro Controls
# ============================================================================
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✨ Pro Controls</div>', unsafe_allow_html=True)
    
    hdr_enabled = st.checkbox("🌈 HDR Mode", value=st.session_state["hdr_enabled"])
    bit_depth = st.radio("Color Depth", ["8-bit", "16-bit"], index=1 if st.session_state["bit_depth"] == "16-bit" else 0, horizontal=True)
    st.session_state["hdr_enabled"] = hdr_enabled
    st.session_state["bit_depth"] = bit_depth
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📷 Camera</div>', unsafe_allow_html=True)
    lens_mm = st.slider("Lens (mm)", 24, 200, 50)
    camera_angle = st.selectbox("Angle", ["eye_level", "low_angle", "high_angle", "dutch"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎨 Style</div>', unsafe_allow_html=True)
    color_palette = st.selectbox("Palette", ["warm_muted", "cool_neutral", "high_contrast", "monochrome"])
    lighting = st.selectbox("Lighting", ["three_point", "dramatic", "soft", "natural"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📐 Composition</div>', unsafe_allow_html=True)
    composition = st.selectbox("Rule", ["rule_of_thirds", "centered", "golden_ratio"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Director Suggestions Panel
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎬 AI Director</div>', unsafe_allow_html=True)
    
    if brief.strip():
        suggestions = director_agent.analyze_scene(brief)
        
        st.markdown(f"**Scene Type:** {suggestions.shot_type.replace('_', ' ').title()}")
        st.markdown(f"**Detected Mood:** {suggestions.mood}")
        
        with st.expander("📷 Camera Suggestions"):
            st.markdown(f"• **Lens:** {suggestions.camera.lens_mm}mm")
            st.markdown(f"• **FOV:** {suggestions.camera.fov_degrees}°")
            st.markdown(f"• **Angle:** {suggestions.camera.angle}")
            st.caption(suggestions.camera.reason)
        
        with st.expander("💡 Lighting"):
            st.markdown(f"• **Setup:** {suggestions.lighting.setup}")
            st.markdown(f"• **Temperature:** {suggestions.lighting.temperature_k}K")
            st.markdown(f"• **Fill:** {suggestions.lighting.fill_intensity}")
            st.caption(suggestions.lighting.reason)
        
        with st.expander("🎨 Color & Style"):
            st.markdown(f"• **Palette:** {suggestions.color.palette}")
            st.markdown(f"• **HDR:** {'Yes' if suggestions.color.hdr else 'No'}")
            st.markdown(f"• **Depth:** {suggestions.color.bit_depth}")
            st.caption(suggestions.color.reason)
        
        if st.button("Apply AI Suggestions", key="apply_ai"):
            # Apply suggestions to session state
            st.session_state["hdr_enabled"] = suggestions.color.hdr
            st.session_state["bit_depth"] = "16-bit" if suggestions.color.bit_depth == "16bit" else "8-bit"
            st.rerun()
    else:
        st.caption("Enter a scene description to get AI suggestions")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# CENTER COLUMN - Canvas
# ============================================================================
with center_col:
    # Single Image Generation
    if single_image_clicked:
        if not brief.strip():
            st.error("Please enter a scene description")
        else:
            with st.spinner("Generating single image with FIBO..."):
                from app.core.client import FiboClient
                client = FiboClient()
                
                # Build prompt with character and FIBO parameters
                full_prompt = f"{character_description}. {brief}. Camera: {lens_mm}mm lens, {camera_angle} angle, {composition} composition."
                if hdr_enabled:
                    full_prompt += " HDR, high dynamic range."
                
                result = client.generate_image(
                    {"prompt": full_prompt},
                    project_id="single_gen",
                    shot_id="image"
                )
                
                if result.get("status") == "success" and os.path.exists(result.get("image_path", "")):
                    st.session_state["single_image_path"] = result["image_path"]
                elif result.get("status") == "offline_placeholder":
                    st.warning("API key not configured.")
                else:
                    st.error(result.get("error", "Generation failed"))
            st.rerun()
    
    # Image-to-Image Generation (FIBO Inspire Mode)
    if img2img_clicked:
        if not char_ref_file:
            st.error("Please upload a reference image for Image-to-Image")
        else:
            with st.spinner("Generating variation with FIBO Inspire Mode..."):
                from app.core.client import FiboClient
                import base64
                client = FiboClient()
                
                # Save the uploaded image temporarily and create a data URL
                temp_path = os.path.join(config.OUTPUT_DIR, "temp_ref.png")
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(char_ref_file.getbuffer())
                
                # Convert to base64 data URL for API
                with open(temp_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                image_url = f"data:image/png;base64,{img_data}"
                
                # Build prompt with modification instructions
                modify_prompt = brief if brief.strip() else "Create a variation of this image"
                full_prompt = f"{modify_prompt}. Camera: {lens_mm}mm lens, {camera_angle} angle."
                if hdr_enabled:
                    full_prompt += " HDR, high dynamic range."
                
                result = client.generate_image(
                    {"prompt": full_prompt, "image_url": image_url},
                    project_id="img2img",
                    shot_id="variation"
                )
                
                if result.get("status") == "success" and os.path.exists(result.get("image_path", "")):
                    st.session_state["img2img_path"] = result["image_path"]
                elif result.get("status") == "offline_placeholder":
                    st.warning("API key not configured.")
                else:
                    st.error(result.get("error", "Generation failed"))
            st.rerun()
    
    # Display Image-to-Image result
    if st.session_state.get("img2img_path") and os.path.exists(st.session_state["img2img_path"]):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔄 Image-to-Image Result</div>', unsafe_allow_html=True)
        st.image(st.session_state["img2img_path"], use_container_width=True)
        with open(st.session_state["img2img_path"], "rb") as f:
            st.download_button("⬇️ Download", f, "img2img_result.png", use_container_width=True, key="dl_img2img")
        if st.button("🔄 Clear", key="clear_img2img"):
            st.session_state["img2img_path"] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display single image if generated
    if st.session_state.get("single_image_path") and os.path.exists(st.session_state["single_image_path"]):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎨 Generated Image</div>', unsafe_allow_html=True)
        st.image(st.session_state["single_image_path"], use_container_width=True)
        with open(st.session_state["single_image_path"], "rb") as f:
            st.download_button("⬇️ Download", f, "generated_image.png", use_container_width=True, key="dl_single")
        if st.button("🔄 Clear", key="clear_single"):
            st.session_state["single_image_path"] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Storyboard Generation
    if generate_clicked:
        if not brief.strip():
            st.error("Please enter a scene description")
        elif not character_description.strip():
            st.error("Please describe your main character")
        else:
            st.session_state["project_name"] = project_name if project_name else "Untitled"
            
            with st.spinner(""):
                st.markdown("<p style='text-align:center; color:#8B3DFF; font-size:1.2rem;'>✨ Creating your storyboard...</p>", unsafe_allow_html=True)
                full_brief = f"[CHARACTER: {character_description.strip()}] {brief.strip()}"
                plan = planner.generate_project_plan(full_brief, mode, num_shots)
                st.session_state["project_plan"] = plan.dict()
                
                ref_path = None
                if char_ref_file:
                    ref_path = os.path.join(config.OUTPUT_DIR, plan.project_id, "char_ref.png")
                    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
                    with open(ref_path, "wb") as f:
                        f.write(char_ref_file.getbuffer())
                
                run_generation(plan, reference_image_path=ref_path)
            st.rerun()
    
    if st.session_state["project_plan"]:
        plan_data = st.session_state["project_plan"]
        current_plan = ProjectPlan(**plan_data)
        outputs = st.session_state.get("outputs", [])
        
        display_name = st.session_state.get("project_name", "Project")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<h2 style="color:#1A1A1A; margin:0;">{display_name}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#6B7280;">{current_plan.brief[:100]}...</p>', unsafe_allow_html=True)
        
        # Tags
        st.markdown(f"""
        <div style="margin: 16px 0;">
            <span class="tag tag-pro">HDR</span>
            <span class="tag">16-bit</span>
            <span class="tag">{lens_mm}mm</span>
            <span class="tag">{len(outputs)} shots</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Grid
        if st.session_state.get("grid_path") and os.path.exists(st.session_state["grid_path"]):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎬 Storyboard</div>', unsafe_allow_html=True)
            st.image(st.session_state["grid_path"], use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with open(st.session_state["grid_path"], "rb") as f:
                    st.download_button("⬇️ PNG", f, "storyboard.png", use_container_width=True)
            with col2:
                if st.button("🎥 Video", use_container_width=True):
                    image_paths = [o["image_path"] for o in outputs if o.get("image_path")]
                    if image_paths:
                        video_path = os.path.join(config.OUTPUT_DIR, current_plan.project_id, "reel.mp4")
                        utils.images_to_video(image_paths, video_path, fps=1)
                        st.session_state["video_path"] = video_path
                        st.rerun()
            with col3:
                if st.button("📄 PDF", use_container_width=True):
                    from app.core.export_tools import create_storyboard_pdf
                    pdf_path = os.path.join(config.OUTPUT_DIR, current_plan.project_id, "storyboard.pdf")
                    shots_data = []
                    for i, out in enumerate(outputs):
                        shot_spec = current_plan.shots[i] if i < len(current_plan.shots) else None
                        shots_data.append({
                            "image_path": out.get("image_path", ""),
                            "description": shot_spec.description if shot_spec else f"Shot {i+1}",
                            "shot_type": shot_spec.shot_type if shot_spec else "Medium",
                            "camera_angle": shot_spec.camera_angle if shot_spec else "Eye Level"
                        })
                    result = create_storyboard_pdf(shots_data, display_name, pdf_path, current_plan.brief)
                    if result:
                        st.session_state["pdf_path"] = result
                        st.success("PDF created!")
                        st.rerun()
            with col4:
                if st.button("💾 Save", use_container_width=True):
                    project_dir = os.path.join(config.OUTPUT_DIR, current_plan.project_id)
                    utils.save_project(project_dir, display_name, plan_data, outputs)
                    st.success("Saved!")
            
            # PDF download if available
            if st.session_state.get("pdf_path") and os.path.exists(st.session_state["pdf_path"]):
                with open(st.session_state["pdf_path"], "rb") as f:
                    st.download_button("📥 Download PDF", f, "storyboard.pdf", use_container_width=True, key="dl_pdf_main")
            
            # Word Document Export button
            doc_col1, doc_col2 = st.columns(2)
            with doc_col1:
                if st.button("📝 Export Word Doc", use_container_width=True, key="btn_docx"):
                    from app.core.export_tools import create_project_document
                    project_dir = os.path.join(config.OUTPUT_DIR, current_plan.project_id)
                    docx_path = os.path.join(project_dir, f"{display_name}_project.docx")
                    settings = {
                        "hdr_enabled": st.session_state.get("hdr_enabled", True),
                        "bit_depth": st.session_state.get("bit_depth", "16-bit"),
                        "lens_mm": lens_mm,
                        "camera_angle": camera_angle,
                        "composition": composition
                    }
                    ref_path = os.path.join(project_dir, "char_ref.png") if os.path.exists(os.path.join(project_dir, "char_ref.png")) else None
                    
                    # Get shots data
                    shots_data = []
                    for i, shot in enumerate(current_plan.shots):
                        shots_data.append({
                            "description": shot.description,
                            "shot_type": shot.shot_type,
                            "camera_angle": shot.camera_angle
                        })
                    
                    doc_path = create_project_document(
                        project_name=display_name,
                        brief=current_plan.brief,
                        character=character_description if character_description else "",
                        shots=shots_data,
                        settings=settings,
                        outputs=outputs,
                        reference_image_path=ref_path,
                        grid_path=st.session_state.get("grid_path"),
                        output_path=docx_path
                    )
                    if doc_path:
                        st.session_state["docx_path"] = doc_path
                        st.success("Word doc created!")
                        st.rerun()
            with doc_col2:
                if st.session_state.get("docx_path") and os.path.exists(st.session_state.get("docx_path", "")):
                    with open(st.session_state["docx_path"], "rb") as f:
                        st.download_button("⬇️ Download .docx", f, f"{display_name}_project.docx", use_container_width=True, key="dl_docx")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Video
        if st.session_state.get("video_path") and os.path.exists(st.session_state["video_path"]):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎥 Video</div>', unsafe_allow_html=True)
            st.video(st.session_state["video_path"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Individual shots with controls
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📸 Individual Shots</div>', unsafe_allow_html=True)
        
        if outputs:
            for i, output in enumerate(outputs):
                img_path = output.get("image_path")
                shot_spec = current_plan.shots[i] if i < len(current_plan.shots) else None
                
                if img_path and os.path.exists(img_path):
                    with st.expander(f"🎬 Shot {i+1}: {shot_spec.shot_type if shot_spec else 'Unknown'}", expanded=i==0):
                        col_img, col_controls = st.columns([2, 1])
                        
                        with col_img:
                            st.image(img_path, use_container_width=True)
                        
                        with col_controls:
                            # Shot info
                            if shot_spec:
                                st.markdown(f"**Type:** {shot_spec.shot_type}")
                                st.markdown(f"**Angle:** {shot_spec.camera_angle}")
                                st.markdown(f"**Framing:** {shot_spec.framing}")
                            
                            # Download button
                            with open(img_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download", 
                                    f, 
                                    f"shot_{i+1}.png", 
                                    key=f"dl_{i}",
                                    use_container_width=True
                                )
                            
                            # Refine button
                            if st.button(f"🔄 Refine", key=f"refine_{i}", use_container_width=True):
                                st.session_state[f"refine_shot_{i}"] = True
                                st.rerun()
                        
                        # Refine UI (if clicked)
                        if st.session_state.get(f"refine_shot_{i}"):
                            st.markdown("---")
                            st.markdown("**🔄 Refine Shot Parameters**")
                            
                            # Editable parameters
                            new_prompt = st.text_area("Prompt", value=shot_spec.description if shot_spec else "", key=f"refine_prompt_{i}", height=80)
                            
                            pcol1, pcol2 = st.columns(2)
                            with pcol1:
                                new_angle = st.selectbox("Camera Angle", ["eye_level", "low_angle", "high_angle", "dutch"], key=f"refine_angle_{i}")
                                new_lens = st.slider("Lens (mm)", 24, 200, 50, key=f"refine_lens_{i}")
                            with pcol2:
                                new_temp = st.slider("Color Temp (K)", 2700, 6500, 5500, key=f"refine_temp_{i}")
                                new_palette = st.selectbox("Palette", ["teal_orange", "golden_hour", "noir", "moody_blue", "natural"], key=f"refine_palette_{i}")
                            
                            rcol1, rcol2 = st.columns(2)
                            with rcol1:
                                if st.button("✨ Regenerate", key=f"regen_{i}", type="primary", use_container_width=True):
                                    with st.spinner("Regenerating shot with FIBO..."):
                                        from app.core.client import FiboClient
                                        client = FiboClient()
                                        
                                        # Build prompt with new parameters
                                        full_prompt = f"{new_prompt}. Camera: {new_lens}mm lens, {new_angle} angle. Color palette: {new_palette}. Color temperature: {new_temp}K."
                                        
                                        result = client.generate_image(
                                            {"prompt": full_prompt},
                                            project_id=current_plan.project_id,
                                            shot_id=f"refined_{i+1}"
                                        )
                                        
                                        if result.get("status") == "success":
                                            # Update the outputs list
                                            outputs[i]["image_path"] = result["image_path"]
                                            st.session_state["outputs"] = outputs
                                            st.session_state[f"refine_shot_{i}"] = False
                                            st.success("Shot regenerated!")
                                            st.rerun()
                                        else:
                                            st.error(result.get("error", "Regeneration failed"))
                            with rcol2:
                                if st.button("❌ Cancel", key=f"cancel_{i}", use_container_width=True):
                                    st.session_state[f"refine_shot_{i}"] = False
                                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Welcome
        st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">Create <span class="welcome-highlight">stunning</span> storyboards</h1>
            <p class="welcome-subtitle">
                Turn your ideas into cinematic storyboards with AI. Add your scene, character, and hit create!
            </p>
            <div>
                <span class="tag tag-pro">✨ HDR</span>
                <span class="tag">16-bit Color</span>
                <span class="tag">Pro Camera</span>
                <span class="tag">AI-Powered</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ADVANCED FEATURES SECTION
# ============================================================================
st.markdown("---")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🚀 Advanced Features</div>', unsafe_allow_html=True)

adv_tabs = st.tabs(["🎞️ Timeline", "🎬 Shot Suggestions", "🎤 Voice Input", "🎨 Mood Board"])

with adv_tabs[0]:
    st.markdown("**Timeline View** - Visual shot sequence")
    if st.session_state.get("outputs"):
        outputs = st.session_state.get("outputs", [])
        # Create horizontal timeline
        st.markdown("""
        <style>
        .timeline { display: flex; gap: 8px; overflow-x: auto; padding: 10px 0; }
        .timeline-shot { flex-shrink: 0; text-align: center; }
        .timeline-shot img { width: 120px; height: 80px; object-fit: cover; border-radius: 8px; border: 2px solid #8B3DFF; }
        .timeline-label { font-size: 0.75rem; color: #9CA3AF; margin-top: 4px; }
        </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(outputs) if len(outputs) <= 8 else 8)
        for i, out in enumerate(outputs[:8]):
            with cols[i]:
                if out.get("image_path") and os.path.exists(out.get("image_path", "")):
                    st.image(out["image_path"], caption=f"Shot {i+1}", width=120)
    else:
        st.caption("Generate a storyboard to see timeline view")

with adv_tabs[1]:
    st.markdown("**AI Shot Suggestions** - Get camera recommendations")
    shot_scene = st.text_input("Describe your scene", placeholder="A chase through a rainy city at night...", key="shot_suggest_input")
    if shot_scene and st.button("🎬 Get Suggestions", key="btn_shot_suggest"):
        from app.core.export_tools import get_shot_type_suggestions
        suggestions = get_shot_type_suggestions(shot_scene)
        for sug in suggestions:
            st.markdown(f"""
            <div style="background: #8B3DFF10; border-left: 3px solid #8B3DFF; padding: 10px; margin: 8px 0; border-radius: 0 8px 8px 0;">
                <strong style="color: #8B3DFF;">{sug['shot_type']}</strong><br>
                <span style="color: #6B7280;">{sug['reason']}</span><br>
                <span style="color: #9CA3AF; font-size: 0.85rem;">📷 {sug['camera']}</span>
            </div>
            """, unsafe_allow_html=True)

with adv_tabs[2]:
    st.markdown("**Voice-to-Storyboard** - Speak your scene")
    st.markdown("""
    <div style="background: #1a102880; padding: 15px; border-radius: 12px; text-align: center;">
        <p style="color: #B794F6; margin-bottom: 10px;">🎤 Click to start voice input</p>
        <p style="color: #9CA3AF; font-size: 0.85rem;">Uses your browser's speech recognition</p>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript for speech recognition
    st.markdown("""
    <script>
    function startVoice() {
        if ('webkitSpeechRecognition' in window) {
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                var text = event.results[0][0].transcript;
                // Would need to use Streamlit's component communication
                alert('You said: ' + text);
            };
            recognition.start();
        } else {
            alert('Voice input not supported in this browser');
        }
    }
    </script>
    """, unsafe_allow_html=True)
    
    voice_text = st.text_area("Or type your scene here:", placeholder="Describe your scene...", key="voice_input", height=80)
    if voice_text and st.button("✨ Generate from Voice", key="btn_voice"):
        st.session_state["brief_input"] = voice_text
        st.success("Scene added! Go to Brief mode to generate.")

with adv_tabs[3]:
    st.markdown("**Mood Board Generator** - Create style references")
    mood_brief = st.text_input("Scene description", placeholder="A cyberpunk city at night...", key="mood_brief")
    mood_char = st.text_input("Character style", placeholder="A hacker in neon clothes...", key="mood_char")
    
    if mood_brief and st.button("🎨 Generate Mood Board", key="btn_mood"):
        from app.core.export_tools import generate_mood_board_prompts
        prompts = generate_mood_board_prompts(mood_brief, mood_char)
        st.markdown("**Generated Prompts for Mood Board:**")
        for i, prompt in enumerate(prompts):
            with st.expander(f"Prompt {i+1}: {['Color/Atmosphere', 'Character Style', 'Location', 'Lighting'][i]}"):
                st.code(prompt)
                st.caption("Copy this prompt and use it with Single Image generation")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PRO TOOLS - Advanced Editing Features
# ============================================================================
st.markdown("---")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🛠️ Pro Tools (Bria API V2)</div>', unsafe_allow_html=True)

pro_tool_tabs = st.tabs(["🔲 Remove BG", "🎨 Gen Fill", "🧹 Eraser", "🖼️ Expand", "✨ Enhance"])

with pro_tool_tabs[0]:
    st.markdown("**Remove Background** - Isolate subjects with RMBG 2.0")
    bg_image = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], key="bg_remove_img")
    if bg_image and st.button("🔲 Remove Background", key="btn_rmbg"):
        with st.spinner("Removing background..."):
            from app.core.client import FiboClient
            client = FiboClient()
            temp_path = os.path.join(config.OUTPUT_DIR, "temp_bg_input.png")
            output_path = os.path.join(config.OUTPUT_DIR, "bg_removed.png")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(bg_image.getbuffer())
            result = client.remove_background(temp_path, output_path)
            if result.get("status") == "success":
                st.image(output_path, caption="Background Removed")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download", f, "no_background.png", key="dl_rmbg")
            else:
                st.error(result.get("error", "Failed"))

with pro_tool_tabs[1]:
    st.markdown("**Generative Fill** - Replace masked areas with AI content")
    gf_col1, gf_col2 = st.columns(2)
    with gf_col1:
        gf_image = st.file_uploader("Original Image", type=["png", "jpg", "jpeg"], key="gf_img")
    with gf_col2:
        gf_mask = st.file_uploader("Mask (white = fill area)", type=["png", "jpg", "jpeg"], key="gf_mask")
    gf_prompt = st.text_input("Fill with", placeholder="a beautiful sunset sky", key="gf_prompt")
    if gf_image and gf_mask and gf_prompt and st.button("🎨 Generate Fill", key="btn_genfill"):
        with st.spinner("Generating fill..."):
            from app.core.client import FiboClient
            client = FiboClient()
            img_path = os.path.join(config.OUTPUT_DIR, "temp_gf_img.png")
            mask_path = os.path.join(config.OUTPUT_DIR, "temp_gf_mask.png")
            output_path = os.path.join(config.OUTPUT_DIR, "gen_filled.png")
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(gf_image.getbuffer())
            with open(mask_path, "wb") as f:
                f.write(gf_mask.getbuffer())
            result = client.generative_fill(img_path, mask_path, gf_prompt, output_path)
            if result.get("status") == "success":
                st.image(output_path, caption="Generative Fill Result")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download", f, "gen_filled.png", key="dl_genfill")
            else:
                st.error(result.get("error", "Failed"))

with pro_tool_tabs[2]:
    st.markdown("**Eraser** - Remove objects and fill intelligently")
    er_col1, er_col2 = st.columns(2)
    with er_col1:
        er_image = st.file_uploader("Original Image", type=["png", "jpg", "jpeg"], key="er_img")
    with er_col2:
        er_mask = st.file_uploader("Mask (white = erase area)", type=["png", "jpg", "jpeg"], key="er_mask")
    if er_image and er_mask and st.button("🧹 Erase Objects", key="btn_eraser"):
        with st.spinner("Erasing..."):
            from app.core.client import FiboClient
            client = FiboClient()
            img_path = os.path.join(config.OUTPUT_DIR, "temp_er_img.png")
            mask_path = os.path.join(config.OUTPUT_DIR, "temp_er_mask.png")
            output_path = os.path.join(config.OUTPUT_DIR, "erased.png")
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(er_image.getbuffer())
            with open(mask_path, "wb") as f:
                f.write(er_mask.getbuffer())
            result = client.erase_object(img_path, mask_path, output_path)
            if result.get("status") == "success":
                st.image(output_path, caption="Erased Result")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download", f, "erased.png", key="dl_eraser")
            else:
                st.error(result.get("error", "Failed"))

with pro_tool_tabs[3]:
    st.markdown("**Expand Image** - Outpainting to extend borders")
    ex_image = st.file_uploader("Upload image to expand", type=["png", "jpg", "jpeg"], key="ex_img")
    ex_ratio = st.selectbox("Target Aspect Ratio", ["16:9", "21:9", "4:3", "1:1", "9:16"], key="ex_ratio")
    if ex_image and st.button("🖼️ Expand Image", key="btn_expand"):
        with st.spinner("Expanding image..."):
            from app.core.client import FiboClient
            client = FiboClient()
            temp_path = os.path.join(config.OUTPUT_DIR, "temp_expand.png")
            output_path = os.path.join(config.OUTPUT_DIR, "expanded.png")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(ex_image.getbuffer())
            result = client.expand_image(temp_path, output_path, ex_ratio)
            if result.get("status") == "success":
                st.image(output_path, caption=f"Expanded to {ex_ratio}")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download", f, "expanded.png", key="dl_expand")
            else:
                st.error(result.get("error", "Failed"))

with pro_tool_tabs[4]:
    st.markdown("**Enhance** - Upscale and improve image quality")
    en_image = st.file_uploader("Upload image to enhance", type=["png", "jpg", "jpeg"], key="en_img")
    if en_image and st.button("✨ Enhance Image", key="btn_enhance"):
        with st.spinner("Enhancing image..."):
            from app.core.client import FiboClient
            client = FiboClient()
            temp_path = os.path.join(config.OUTPUT_DIR, "temp_enhance.png")
            output_path = os.path.join(config.OUTPUT_DIR, "enhanced.png")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(en_image.getbuffer())
            result = client.enhance_image(temp_path, output_path)
            if result.get("status") == "success":
                st.image(output_path, caption="Enhanced Image")
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download", f, "enhanced.png", key="dl_enhance")
            else:
                st.error(result.get("error", "Failed"))

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="footer-bar">
    <p class="footer-text">
        Built for <a href="#" class="footer-link">FIBO Hackathon 2024</a> | 
        Powered by <a href="https://bria.ai" class="footer-link">Bria FIBO</a>
    </p>
</div>
""", unsafe_allow_html=True)
