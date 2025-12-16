"""Gallery Page - View generated outputs."""
import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.utils import helpers as utils
from app.models import config

st.set_page_config(page_title="Gallery - MindLens", page_icon="🖼️", layout="wide")

st.markdown("# 🖼️ Gallery")
st.markdown("Your generated storyboards and outputs")
st.markdown("---")

# Get all saved projects
saved_projects = utils.list_saved_projects(config.OUTPUT_DIR)

if saved_projects:
    st.success(f"📁 Found {len(saved_projects)} project(s)")
    
    for proj in saved_projects:
        with st.expander(f"📁 **{proj['project_name']}**", expanded=True):
            proj_data = utils.load_project(proj['path'])
            
            if proj_data:
                # Show project info
                if proj_data.get('plan'):
                    plan = proj_data['plan']
                    st.caption(f"Brief: {plan.get('brief', 'N/A')[:100]}...")
                
                # Show grid if available
                project_dir = proj['path']
                grid_files = [f for f in os.listdir(project_dir) if f.startswith('grid_') and f.endswith('.png')]
                if grid_files:
                    grid_path = os.path.join(project_dir, grid_files[0])
                    st.image(grid_path, caption="Storyboard Grid", use_container_width=True)
                
                # Show individual shots
                if proj_data.get('outputs'):
                    st.markdown("**Individual Shots:**")
                    cols = st.columns(min(len(proj_data['outputs']), 4))
                    for i, out in enumerate(proj_data['outputs'][:8]):
                        with cols[i % 4]:
                            img_path = out.get('image_path', '')
                            if img_path and os.path.exists(img_path):
                                st.image(img_path, caption=f"Shot {i+1}", use_container_width=True)
                            else:
                                st.caption(f"Shot {i+1}: Image not found")
                else:
                    st.caption("No output images found in this project")
            else:
                st.warning("Could not load project data")
            
            st.markdown("---")
else:
    st.info("🎨 **No projects yet!**")
    st.markdown("""
    Generate a storyboard from the main page to see your outputs here.
    
    1. Go to **🏠 Home** (main page)
    2. Enter a scene description
    3. Click **✨ Storyboard** to generate
    4. Your creations will appear here!
    """)

st.markdown("---")
st.caption("Powered by Bria FIBO API | Product by Snigdha")
