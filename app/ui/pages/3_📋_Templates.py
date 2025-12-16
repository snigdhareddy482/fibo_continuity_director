"""Templates Page - Ready-to-use presets."""
import streamlit as st

st.set_page_config(page_title="Templates - MindLens", page_icon="📋", layout="wide")

st.markdown("# 📋 Templates")
st.markdown("Ready-to-use scene presets - click to load, then go to Home to generate!")
st.markdown("---")

# Storyboard Templates
st.markdown("## 🎬 Storyboard Templates")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎭 Drama")
    st.caption("Intense, emotional scenes with dramatic lighting")
    if st.button("Load Drama", key="t_drama", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "A tense confrontation in a dimly lit interrogation room. Detective Sarah leans forward, her face half in shadow, casting long shadows across the table."
        st.session_state["char_input"] = "Detective Sarah, a seasoned investigator in her 40s with sharp eyes, wearing a dark blazer and detective badge"
        st.success("✅ Loaded! Go to Home page and click Storyboard")
    
    st.markdown("---")
    
    st.markdown("### 🔮 Sci-Fi")
    st.caption("Futuristic settings with advanced technology")
    if st.button("Load Sci-Fi", key="t_scifi", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "A lone astronaut stands on the edge of a glass observation deck aboard a massive space station, staring at a dying star. Holographic displays flicker around them showing critical warnings."
        st.session_state["char_input"] = "Commander Maya Chen, wearing a sleek white spacesuit with blue accents, helmet off, short dark hair, determined expression"
        st.success("✅ Loaded! Go to Home page and click Storyboard")

with col2:
    st.markdown("### 🌅 Romance")
    st.caption("Warm, intimate moments with soft lighting")
    if st.button("Load Romance", key="t_romance", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "Golden hour on a rooftop garden overlooking the city skyline. Two lovers share their first dance as fairy lights twinkle around them and the sun sets in warm orange hues."
        st.session_state["char_input"] = "Maya, a young artist in her late 20s with flowing auburn hair and paint-stained fingers, wearing a bohemian dress with floral patterns"
        st.success("✅ Loaded! Go to Home page and click Storyboard")
    
    st.markdown("---")
    
    st.markdown("### 🎃 Horror")
    st.caption("Dark, atmospheric scenes with tension")
    if st.button("Load Horror", key="t_horror", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "An abandoned Victorian mansion at midnight. Moonlight streams through broken windows as a shadowy figure emerges from the darkness. Dust particles float in the pale light."
        st.session_state["char_input"] = "Emma, a young woman in her 20s with pale skin and fearful wide eyes, wearing a torn white dress, hair disheveled"
        st.success("✅ Loaded! Go to Home page and click Storyboard")

with col3:
    st.markdown("### ⚔️ Action")
    st.caption("Dynamic, high-energy sequences")
    if st.button("Load Action", key="t_action", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "A warrior stands at the edge of a cliff overlooking a vast battlefield, ancient sword drawn and gleaming. An army of shadows approaches from below as lightning cracks across the stormy sky."
        st.session_state["char_input"] = "Kai, a battle-scarred warrior in his 30s with silver hair tied back, wearing weathered bronze armor and a flowing crimson cloak"
        st.success("✅ Loaded! Go to Home page and click Storyboard")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Product")
    st.caption("Clean, professional product shots")
    if st.button("Load Product", key="t_product", use_container_width=True, type="primary"):
        st.session_state["brief_input"] = "A sleek smartphone floating on a gradient background with soft reflections below. Premium studio lighting highlights the device's curves and the brilliant AMOLED display."
        st.session_state["char_input"] = "Premium smartphone with glass back, titanium frame, edge-to-edge AMOLED display showing vibrant colors"
        st.success("✅ Loaded! Go to Home page and click Storyboard")

st.markdown("---")
st.markdown("## 📜 Script Template")

if st.button("Load Sample Script", key="t_script", type="secondary"):
    st.session_state["script_input"] = """INT. COFFEE SHOP - DAY

SARAH (30s, nervous) enters the bustling coffee shop, scanning the room anxiously.

SARAH
(to herself)
I've been waiting for this moment for so long.

She spots DAVID (40s, confident) standing from a corner booth, a warm smile spreading across his face.

DAVID
So have I.

They embrace as golden sunlight streams through the window, illuminating them in a warm glow.

FADE OUT."""
    st.success("✅ Script loaded! Go to Home, select 'Script' mode, and paste")

st.markdown("---")
st.caption("Powered by Bria FIBO API | Product by Snigdha")
