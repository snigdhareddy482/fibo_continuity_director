"""Features Page - All MindLens capabilities."""
import streamlit as st

st.set_page_config(page_title="Features - MindLens", page_icon="✨", layout="wide")

st.markdown("# ✨ MindLens Features")
st.markdown("---")

# Core Features
st.markdown("## 🎯 Core Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎬 AI Storyboard Generation
    - **Text-to-Image** with FIBO API
    - Professional shot composition
    - HDR and 16-bit color support
    - Structured prompts for consistency
    
    ### 🔄 Inspire Mode (Image-to-Image)
    - Upload reference images
    - Generate style variations
    - Maintain visual consistency
    """)

with col2:
    st.markdown("""
    ### 🎭 AI Director
    - Scene analysis with reasoning
    - Smart camera angle suggestions
    - Lighting recommendations
    - Composition guidance
    
    ### 📜 Script Parser
    - Paste industry-standard screenplay
    - Auto-extract scenes & characters
    - Convert to storyboard shots
    """)

with col3:
    st.markdown("""
    ### 🎬 Story Arc Generator
    - Hero's Journey templates
    - Rise & Fall narratives
    - Love story structures
    
    ### 🎨 Style DNA Extractor
    - Extract color palettes
    - Learn visual styles
    - Maintain consistency
    """)

st.markdown("---")
st.markdown("## 🛠️ Pro Tools (Bria API V2)")

pro_col1, pro_col2, pro_col3 = st.columns(3)
with pro_col1:
    st.info("🔲 **Background Removal** - RMBG 2.0 for clean cutouts")
    st.info("🎨 **Generative Fill** - AI-powered inpainting")
with pro_col2:
    st.info("🧹 **Eraser** - Intelligent object removal")
    st.info("🖼️ **Expand** - Outpainting to extend borders")
with pro_col3:
    st.info("✨ **Enhance** - Upscaling and quality improvement")
    st.info("📷 **Pro Camera** - Lens and angle control")

st.markdown("---")
st.markdown("## 📤 Export Options")
st.markdown("""
| Format | Description |
|--------|-------------|
| 📄 **PDF Storyboard** | Professional layout with thumbnails and descriptions |
| 🎥 **Video Export** | Slideshow with transitions |
| 📝 **Word Document** | Complete project with embedded images |
| 🖼️ **PNG Grid** | Storyboard overview image |
""")

st.markdown("---")
st.caption("Powered by Bria FIBO API | Product by Snigdha")
