import logging
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Tuple
from ..models import config
from . import engine as continuity_engine
from . import client as fibo_client
from ..models.schemas import ProjectPlan

logger = logging.getLogger(__name__)

# Instantiate client for auto-fix
client = fibo_client.FiboClient()

def get_avg_color(image_path: str) -> Tuple[float, float, float]:
    """
    Computes the average HSV color of an image.
    Returns (H, S, V) normalized to [0, 1].
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("HSV")
            img = img.resize((64, 64)) # Downsample for performance
            arr = np.array(img) / 255.0 # Normalize to 0-1
            
            # Compute mean across height and width
            mean_color = np.mean(arr, axis=(0, 1))
            return tuple(mean_color)
    except Exception as e:
        logger.error(f"Error calculating avg color for {image_path}: {e}")
        return (0.0, 0.0, 0.0)

def color_distance(c1: Tuple[float, float, float], c2: Tuple[float, float, float]) -> float:
    """
    Computes Euclidean distance between two HSV vectors.
    """
    return float(np.linalg.norm(np.array(c1) - np.array(c2)))

def validate_continuity(outputs: List[Dict[str, Any]], tolerance: float = None) -> List[Dict[str, Any]]:
    """
    Validates visual continuity (color consistency) across a sequence of outputs.
    Compares each shot to the first shot (reference).
    """
    if not outputs:
        return outputs
        
    if tolerance is None:
        tolerance = config.COLOR_TOLERANCE
    
    # Use the first image as the reference for style/color continuity
    ref_image_path = outputs[0].get("image_path")
    if not ref_image_path:
        logger.warning("No image path for first shot, skipping validation.")
        return outputs
        
    ref_color = get_avg_color(ref_image_path)
    
    for i, output in enumerate(outputs):
        # Skip checking the first one against itself (distance is 0)
        # but we iterate all to set consistent keys
        
        image_path = output.get("image_path")
        if not image_path:
             output["continuity_score"] = 0.0
             output["continuity_ok"] = False
             continue
             
        cur_color = get_avg_color(image_path)
        diff = color_distance(ref_color, cur_color)
        
        # Simple score: 1.0 is perfect match, 0.0 is far apart
        # Max theoretical distance in unit cube is sqrt(3) ~ 1.732
        score = max(0.0, 1.0 - (diff / 1.732)) 
        
        # User requested 1.0 - diff for simple approx, but let's stick to their formula concept
        # diff is raw euclidean distance
        continuity_score = max(0.0, 1.0 - diff)
        
        output["continuity_score"] = continuity_score
        output["continuity_ok"] = diff <= tolerance
        output["color_diff"] = diff
        
    return outputs

def auto_fix_continuity(project_plan: ProjectPlan, outputs: List[Dict[str, Any]], tolerance: float = None) -> List[Dict[str, Any]]:
    """
    Attempts to fix shots that failed continuity validation by regenerating them
    with reinforced style prompts.
    """
    # 1. Ensure scores are up to date
    outputs = validate_continuity(outputs, tolerance)
    
    for output in outputs:
        if not output.get("continuity_ok", False):
            shot_id = output.get("shot_id")
            logger.info(f"Auto-fixing continuity for shot {shot_id} (Score: {output.get('continuity_score'):.2f})")
            
            # Find the shot spec
            shot = next((s for s in project_plan.shots if s.shot_id == shot_id), None)
            if not shot:
                continue
                
            # Reinforce prompt via description modification
            # We create a temporary modified shot object to avoid mutating the original plan permanently
            # or just mutate it? Let's clone/copy loosely.
            original_description = shot.description
            shot.description += " with the same warm muted color palette and lighting as the first shot."
            
            try:
                # Re-build payload
                payload = continuity_engine.build_fibo_payload(project_plan.continuity_map, shot)
                
                # Regenerate
                result = client.generate_image(payload, project_plan.project_id, shot.shot_id)
                
                # Update output entry
                output["image_path"] = result.get("image_path")
                output["payload"] = payload
                output["re_rendered"] = True
                
                # Re-validate this single shot
                ref_image_path = outputs[0].get("image_path")
                if ref_image_path:
                    ref_color = get_avg_color(ref_image_path)
                    cur_color = get_avg_color(result.get("image_path"))
                    diff = color_distance(ref_color, cur_color)
                    output["continuity_score"] = max(0.0, 1.0 - diff)
                    output["continuity_ok"] = diff <= (tolerance or config.COLOR_TOLERANCE)
                    output["color_diff"] = diff
                    
                logger.info(f"Fixed shot {shot_id}. New Score: {output.get('continuity_score'):.2f}")
                
            except Exception as e:
                logger.error(f"Failed to auto-fix shot {shot_id}: {e}")
            finally:
                # Restore description if we don't want to persist the hack
                shot.description = original_description

    return outputs
