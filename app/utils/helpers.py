"""Helper utilities for media processing, project persistence, and file operations."""
import os
import re
import uuid
import math
import json
import logging
from typing import List
from PIL import Image

# MoviePy is imported lazily in images_to_video() to avoid startup hang

logger = logging.getLogger(__name__)

def create_storyboard_grid(image_paths: List[str], output_path: str, grid_cols: int = None) -> str:
    """
    Creates a storyboard grid (contact sheet) PNG from the given image paths.
    - Resizes images to a common thumbnail size.
    - Dynamically calculates optimal grid layout if grid_cols is None.
    - Arranges them in grid_cols columns and enough rows.
    - Adds branding to empty cells.
    - Saves to output_path.
    - Returns output_path.
    """
    from PIL import ImageDraw, ImageFont
    
    valid_paths = [p for p in image_paths if os.path.exists(p)]
    
    if not valid_paths:
        logger.warning("No valid images provided for storyboard grid.")
        return ""

    try:
        images = [Image.open(p).convert("RGB") for p in valid_paths]
        n_images = len(images)
        
        # Dynamically choose grid columns based on image count to avoid empty cells
        if grid_cols is None:
            if n_images == 1:
                grid_cols = 1
            elif n_images == 2:
                grid_cols = 2
            elif n_images <= 4:
                grid_cols = 2
            elif n_images <= 6:
                grid_cols = 3
            elif n_images <= 8:
                grid_cols = 4
            else:
                grid_cols = min(5, math.ceil(math.sqrt(n_images)))
        
        # Define uniform thumbnail size
        thumb_w = 320
        ratio = images[0].height / images[0].width
        thumb_h = int(thumb_w * ratio)
        
        # Resize all
        thumbs = [img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS) for img in images]
        
        n_rows = math.ceil(n_images / grid_cols)
        
        # Calculate empty cells
        total_cells = n_rows * grid_cols
        empty_cells = total_cells - n_images
        
        # Create full grid
        grid_w = grid_cols * thumb_w
        grid_h = n_rows * thumb_h
        grid_img = Image.new("RGB", (grid_w, grid_h), (30, 20, 50))  # Dark purple background
        
        # Paste images
        for idx, thumb in enumerate(thumbs):
            row = idx // grid_cols
            col = idx % grid_cols
            x = col * thumb_w
            y = row * thumb_h
            grid_img.paste(thumb, (x, y))
        
        # Create branding for empty cells
        if empty_cells > 0:
            draw = ImageDraw.Draw(grid_img)
            
            # Try to use a nicer font, fallback to default
            try:
                font_large = ImageFont.truetype("arial.ttf", 18)
                font_small = ImageFont.truetype("arial.ttf", 14)
                font_watermark = ImageFont.truetype("arial.ttf", 28)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
                font_watermark = ImageFont.load_default()
            
            # Fill empty cells with branding
            for cell_idx in range(n_images, total_cells):
                row = cell_idx // grid_cols
                col = cell_idx % grid_cols
                x = col * thumb_w
                y = row * thumb_h
                
                # Draw dark branded cell background
                draw.rectangle([x, y, x + thumb_w, y + thumb_h], fill=(25, 15, 45))
                
                # Draw watermark in background (low visibility)
                watermark_text = "MindLens"
                draw.text((x + thumb_w//2 - 50, y + thumb_h//2 - 40), watermark_text, 
                         fill=(60, 40, 80), font=font_watermark)
                
                # Draw "Sponsored by Bria FIBO"
                draw.text((x + 20, y + thumb_h//2 - 15), "Sponsored by", 
                         fill=(120, 100, 150), font=font_small)
                draw.text((x + 20, y + thumb_h//2 + 5), "Bria FIBO", 
                         fill=(139, 61, 255), font=font_large)
                
                # Draw "Product by Snigdha"
                draw.text((x + 20, y + thumb_h//2 + 40), "Product by Snigdha", 
                         fill=(150, 130, 180), font=font_small)
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        grid_img.save(output_path)
        logger.info(f"Storyboard grid saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create storyboard grid: {e}")
        return ""

def images_to_video(image_paths: List[str], output_path: str, fps: int = 1) -> str:
    """
    Creates an MP4 video from the given list of image paths using MoviePy.
    Each image is shown for 1/fps seconds.
    Saves the video to output_path and returns output_path.
    """
    # Lazy import MoviePy to avoid startup hang
    ImageSequenceClip = None
    try:
        from moviepy import ImageSequenceClip
    except ImportError:
        try:
            from moviepy.editor import ImageSequenceClip
        except ImportError:
            logger.error("MoviePy is not installed. Cannot create video.")
            return ""
    
    if ImageSequenceClip is None:
        logger.error("MoviePy is not installed/working. Cannot create video.")
        return ""
        
    valid_paths = [p for p in image_paths if os.path.exists(p)]
    
    if not valid_paths:
        logger.warning("No valid images provided for video.")
        return ""
    
    try:
        logger.info(f"Creating video from {len(valid_paths)} images at {fps} fps...")
        
        clip = ImageSequenceClip(valid_paths, fps=fps)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write file
        # logger=None to suppress moviepy's verbose output unless needed
        clip.write_videofile(output_path, codec="libx264", audio=False, logger=None)
        
        logger.info(f"Video saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        return ""

def safe_project_id_from_brief(brief: str) -> str:
    """
    Generates a filesystem-safe project_id from the brief:
    - Lowercase
    - Keep a few words
    - Replace spaces with underscores
    - Append a short UUID suffix
    """
    # Clean string: remove non-alphanumeric/spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', brief)
    
    # Split and take first ~5 words
    words = cleaned.split()
    prefix = "_".join(words[:5]).lower()
    
    if not prefix:
        prefix = "project"
    
    # Generate suffix
    suffix = str(uuid.uuid4())[:8]
    
    return f"{prefix}_{suffix}"


def save_project(project_dir: str, project_name: str, plan_dict: dict, outputs: list) -> str:
    """
    Saves the project state to a JSON file for later loading.
    Returns the path to the saved file.
    """
    
    save_data = {
        "project_name": project_name,
        "plan": plan_dict,
        "outputs": outputs,
        "saved_at": str(uuid.uuid4())[:8]  # Simple version marker
    }
    
    save_path = os.path.join(project_dir, "project_state.json")
    os.makedirs(project_dir, exist_ok=True)
    
    with open(save_path, "w") as f:
        json.dump(save_data, f, indent=2)
    
    logger.info(f"Project saved to {save_path}")
    return save_path


def load_project(project_dir: str) -> dict:
    """
    Loads a project state from a JSON file.
    Returns dict with keys: project_name, plan, outputs
    """
    
    load_path = os.path.join(project_dir, "project_state.json")
    
    if not os.path.exists(load_path):
        return None
    
    with open(load_path, "r") as f:
        data = json.load(f)
    
    logger.info(f"Project loaded from {load_path}")
    return data


def list_saved_projects(base_dir: str) -> List[dict]:
    """
    Lists all saved projects in the outputs directory.
    Returns list of dicts with project_id, project_name, and path.
    """
    
    projects = []
    if not os.path.exists(base_dir):
        return projects
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        state_file = os.path.join(item_path, "project_state.json")
        
        if os.path.isdir(item_path) and os.path.exists(state_file):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                projects.append({
                    "project_id": item,
                    "project_name": data.get("project_name", item),
                    "path": item_path
                })
            except:
                pass  # Skip corrupted files
    
    return projects
