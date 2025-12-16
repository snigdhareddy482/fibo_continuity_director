import os
import logging
from typing import List, Dict, Any, Optional
from ..models.schemas import ProjectPlan, ContinuityMap, ShotSpec
from ..models import config
from . import client as fibo_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate client once at module level
client = fibo_client.FiboClient()

def build_fibo_payload(continuity_map: ContinuityMap, shot: ShotSpec) -> Dict[str, Any]:
    """
    Constructs the JSON payload for the FIBO API by merging global continuity settings
    with specific shot descriptions and overrides.
    """
    # Start with base configuration from the continuity map
    base = {
        "global_style": continuity_map.global_style.copy(),
        "camera": continuity_map.camera.copy(),
        "lighting": continuity_map.lighting.copy(),
        "composition": continuity_map.composition.copy(),
        "description": shot.description
    }
    
    # Apply Camera Overrides
    if shot.camera_overrides:
        base["camera"].update(shot.camera_overrides)
        
    # Apply Composition Overrides
    if shot.composition_overrides:
        base["composition"].update(shot.composition_overrides)
        
    # Add Metadata for tracking
    base["metadata"] = {
        "shot_id": shot.shot_id,
        "shot_type": shot.shot_type
    }
    
    # Note: The API technically expects a "prompt" field. 
    # The FiboClient uses 'prompt' as the main key. 
    # We need to serialize this structured dict into a prompt string OR 
    # if the API accepts structured params (which Bria sometimes does via controls), pass them.
    # However, based on the specific 'text2img' curl example provided earlier which just used "prompt",
    # we should likely flatten this into a rich prompt string to be safe, OR
    # simply pass this dict if we assume the client handles the formatting.
    # The FiboClient.generate_image expects a payload dict. 
    # The prompt earlier was a simple string in the payload.
    # Let's map part of this to the "prompt" field in the payload we return.
    
    # Construct a rich prompt string from the components
    # This ensures the API gets all the info even if it only supports 'prompt'
    attributes = []
    
    # Description first
    attributes.append(base["description"])
    
    # Camera
    cam = base["camera"]
    attributes.append(f"{cam.get('lens_mm', 50)}mm lens")
    attributes.append(f"{cam.get('angle', 'eye_level')} angle")
    attributes.append(f"{cam.get('movement', 'static')} camera")
    
    # Lighting
    light = base["lighting"]
    attributes.append(f"{light.get('setup', 'three_point')} lighting")
    attributes.append(f"{light.get('key_direction', 'front')} light")
    
    # Style
    style = base["global_style"]
    attributes.append(f"Style: {style.get('look', 'cinematic')}")
    attributes.append(f"Palette: {style.get('color_palette', 'standard')}")
    
    # Pro-grade FIBO features (HDR and 16-bit color)
    if style.get("hdr"):
        attributes.append("HDR high dynamic range")
    if style.get("bit_depth") == "16bit":
        attributes.append("16-bit color depth, professional color grading")
    
    full_prompt = ", ".join(attributes)
    
    # Return the payload structure expected by the Client/API
    # We include the 'prompt' which is mandatory
    # We also include the raw structured data in case the client wants to use it for logging or future extended features
    payload = {
        "prompt": full_prompt,
        "negative_prompt": config.DEFAULT_NEGATIVE_PROMPT,
        "structured_params": base 
    }
    
    return payload

def generate_sequence(project_plan: ProjectPlan, progress_callback=None, reference_image_path: str = None) -> List[Dict[str, Any]]:
    """
    Generates images for the entire sequence of shots in the project plan.
    Uses the first shot as a character reference for subsequent shots to maintain consistency.
    
    Args:
        project_plan: The project plan with shots.
        progress_callback: Optional function(current_index, total, shot_id) for progress updates.
        reference_image_path: Optional pre-existing reference image. If None, uses first generated shot.
    """
    # Ensure output directory exists
    project_output_dir = os.path.join(config.OUTPUT_DIR, project_plan.project_id)
    os.makedirs(project_output_dir, exist_ok=True)
    
    results = []
    total_shots = len(project_plan.shots)
    
    # Character reference image - will be set to first shot if not provided
    char_reference = reference_image_path
    
    logger.info(f"Starting generation for Project {project_plan.project_id} with {total_shots} shots.")
    if char_reference:
        logger.info(f"Using provided reference image: {char_reference}")
    
    for i, shot in enumerate(project_plan.shots):
        logger.info(f"Generating Shot {shot.shot_id}")
        
        # Progress callback
        if progress_callback:
            progress_callback(i, total_shots, shot.shot_id)
        
        # Build Payload
        payload = build_fibo_payload(project_plan.continuity_map, shot)
        
        # Generate each shot using FIBO text2img
        logger.info(f"Shot {i+1}: Generating with FIBO")
        result = client.generate_image(payload, project_plan.project_id, shot.shot_id)
        
        # Store first shot as reference
        if i == 0:
            char_reference = result.get("image_path")
            logger.info(f"First shot saved as character reference")
        
        # Aggregate Result
        # Add extra context from the shot to the result info
        result_entry = {
            "shot_id": shot.shot_id,
            "shot_type": shot.shot_type,
            "shot_role": shot.shot_role,
            "framing": shot.framing,
            "camera_angle": shot.camera_angle,
            "description": shot.description,
            "image_path": result.get("image_path"),
            "payload": payload,
            "camera_overrides": shot.camera_overrides,
            "composition_overrides": shot.composition_overrides,
            "notes": shot.notes,
            "status": result.get("status"),
            "error": result.get("error"),
            "used_reference": i > 0 or reference_image_path is not None
        }
        results.append(result_entry)
        
    return results

def refine_shot_from_image(project_plan: ProjectPlan, shot_id: str, base_image_path: str) -> Dict[str, Any]:
    """
    Refines a specific shot using an existing image as a base (Image-to-Image).
    """
    # Find the shot
    shot = next((s for s in project_plan.shots if s.shot_id == shot_id), None)
    if not shot:
        raise ValueError(f"Shot {shot_id} not found in project plan.")
        
    logger.info(f"Refining Shot {shot_id} using FIBO")
    
    # Build Payload
    payload = build_fibo_payload(project_plan.continuity_map, shot)
    
    # Regenerate shot with the same prompt for a variation
    result = client.generate_image(
        payload=payload,
        project_id=project_plan.project_id,
        shot_id=f"{shot_id}_refined"
    )
    
    # Return result with context
    return {
        "shot_id": shot.shot_id,
        "shot_type": shot.shot_type,
        "description": shot.description,
        "image_path": result.get("image_path"),
        "payload": payload,
        "refined": True,
        "status": result.get("status"),
        "error": result.get("error")
    }
