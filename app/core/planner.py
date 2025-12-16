import uuid
import json
from typing import List, Dict, Any
from ..models.schemas import ProjectPlan, ShotSpec, ContinuityMap

# The System Prompt for the LLM
PLANNER_SYSTEM_PROMPT = """
You are a cinematic and product photography shot planner for an AI visual generation system called FIBO Continuity Director.

Your job:
- Take a brief describing either:
   - a cinematic scene, or
   - a product catalog situation.
- Design:
   1) A single coherent continuity style:
       - global_style: look, color_palette, hdr (bool), bit_depth ("16bit" or "8bit")
       - camera: lens_mm, fov_degrees, height_m, angle, movement
       - lighting: setup, key_direction, fill_intensity, back_intensity, temperature_k
       - composition: rule, subject_position, depth_of_field
   2) A list of shots:
       - shot_id: "shot_001", "shot_002", ...
       - shot_type: e.g., "wide_establishing", "medium", "close_up", "over_the_shoulder"
       - description: clear visual description, consistent with continuity style
       - camera_overrides: only when needed
       - composition_overrides: only when needed

Rules:
- All shots must feel like they belong to the same scene or product set.
- For mode="product", focus on product angles, close-ups, context shots.
- Use cinematic language for shots where relevant.

Output:
- Return JSON ONLY with this structure:

{
  "continuity_map": {
     "global_style": {...},
     "camera": {...},
     "lighting": {...},
     "composition": {...}
  },
  "shots": [
     {
       "shot_id": "shot_001",
       "shot_type": "...",
       "description": "...",
       "camera_overrides": {...},
       "composition_overrides": {...},
       "notes": {...}
     },
     ...
  ]
}
"""

PLANNER_USER_PROMPT_TEMPLATE = """
mode: "{mode}"               // "storyboard" or "product"
num_shots: {num_shots}

brief:
\"\"\"
{brief}
\"\"\"

Generate a continuity_map and exactly {num_shots} shots that match the schema described in the system prompt.

Return ONLY the JSON object (no comments, no markdown).
"""

def mock_llm_generation(brief: str, mode: str, num_shots: int) -> Dict[str, Any]:
    """
    Simulates the JSON output of the LLM based on the system prompt.
    Uses heuristics to generate varied content based on 'mode'.
    """
    
    # 1. Determine Style based on Mode/Brief
    if mode == "product":
        style = {
            "global_style": {"look": "Studio Product", "color_palette": "clean_minimal", "hdr": True, "bit_depth": "16bit"},
            "camera": {"lens_mm": 85.0, "fov_degrees": 20.0, "height_m": 1.0, "angle": "slightly_above", "movement": "static"},
            "lighting": {"setup": "soft_box", "key_direction": "side_left", "fill_intensity": 0.8, "back_intensity": 0.2, "temperature_k": 5500},
            "composition": {"rule": "centered", "subject_position": "center", "depth_of_field": "deep"}
        }
        shot_templates = [
            ("hero_shot", "Hero shot of the product, fully lit, on a clean background."),
            ("detail_shot", "Close-up detail shot emphasizing texture and material quality."),
            ("lifestyle_context", "The product placed in a stylized environment context."),
            ("packaging_shot", "The product alongside its packaging, elegant arrangement."),
            ("top_down", "Top-down flat lay view of the product elements.")
        ]
    else: # Storyboard / Cinematic
        style = {
            "global_style": {"look": "Cinematic", "color_palette": "teal_orange", "hdr": True, "bit_depth": "16bit"},
            "camera": {"lens_mm": 35.0, "fov_degrees": 50.0, "height_m": 1.6, "angle": "eye_level", "movement": "slow_pan"},
            "lighting": {"setup": "cinematic", "key_direction": "side", "fill_intensity": 0.4, "back_intensity": 0.5, "temperature_k": 4500},
            "composition": {"rule": "rule_of_thirds", "subject_position": "specs", "depth_of_field": "shallow"}
        }
        # Enhanced shot templates with explicit roles, framing, and camera angles
        # Pattern: (shot_type, description, shot_role, framing, camera_angle, composition_rule)
        shot_templates = [
            ("wide_establishing", "Wide establishing shot setting the scene with street background and atmosphere, showing the full environment.",
             "Wide hero introduction", "wide", "low_angle", "wide_establishing"),
            ("medium_character", "Medium shot focusing on the main subject with clear expression and interaction, tighter crop on character.",
             "Medium character affirmation", "medium", "eye_level", "centered"),
            ("over_the_shoulder", "Over-the-shoulder perspective looking at the point of interest, adding depth.",
             "POV transition", "medium", "eye_level", "rule_of_thirds"),
            ("close_up", "Close-up on the subject's face or key detail, emotional and expressive focus.",
             "Emotional close-up", "close_up", "eye_level", "golden_ratio"),
            ("low_angle_hero", "Low angle shot looking up at the subject, creating a sense of power and importance.",
             "Hero power shot", "medium", "low_angle", "rule_of_thirds"),
            ("high_angle_context", "High angle view providing environmental context and scale.",
             "Context overview", "wide", "high_angle", "rule_of_thirds"),
            ("dutch_angle", "Dynamic dutch angle adding energy and visual interest.",
             "Dynamic action", "medium", "dutch", "rule_of_thirds"),
            ("extreme_closeup", "Extreme close-up on a key detail or expression.",
             "Detail emphasis", "extreme_closeup", "eye_level", "centered"),
        ]

    # 2. Generate Shots
    shots = []
    for i in range(num_shots):
        template = shot_templates[i % len(shot_templates)]
        shot_type = template[0]
        base_desc = template[1]
        
        # Extract enhanced fields if present (storyboard mode has 6-tuple, product has 2-tuple)
        if len(template) >= 6:
            shot_role = template[2]
            framing = template[3]
            camera_angle = template[4]
            composition_rule = template[5]
        else:
            # Fallback for product mode or legacy templates
            shot_role = shot_type.replace("_", " ").title()
            framing = "medium"
            camera_angle = "eye_level"
            composition_rule = "centered"
        
        # Merge brief into description
        # Extract character description if present to put it FIRST (important for consistency!)
        if brief.startswith("[CHARACTER:"):
            # Extract character description and remaining brief
            char_end = brief.find("]")
            if char_end != -1:
                character_part = brief[11:char_end].strip()  # Extract just the character desc
                remaining_brief = brief[char_end+1:].strip()
                # Put character first, then shot description, then scene context
                full_desc = f"{character_part}. {base_desc} Scene: {remaining_brief}"
            else:
                full_desc = f"{base_desc} Context: {brief}"
        else:
            full_desc = f"{base_desc} Context: {brief}"
        
        # Build camera overrides based on framing and angle
        camera_overrides = {"angle": camera_angle}
        if framing == "wide":
            camera_overrides["lens_mm"] = 24.0
            camera_overrides["fov_degrees"] = 70.0
        elif framing == "close_up":
            camera_overrides["lens_mm"] = 85.0
            camera_overrides["fov_degrees"] = 25.0
        elif framing == "extreme_closeup":
            camera_overrides["lens_mm"] = 100.0
            camera_overrides["fov_degrees"] = 18.0
        
        # Build composition overrides
        composition_overrides = {"rule": composition_rule}
        
        shots.append({
            "shot_id": f"shot_{i+1:03d}",
            "shot_type": shot_type,
            "description": full_desc,
            "shot_role": shot_role,
            "framing": framing,
            "camera_angle": camera_angle,
            "camera_overrides": camera_overrides,
            "composition_overrides": composition_overrides,
            "notes": {"continuity_kept": ["palette", "lighting", "time_of_day"], "varied": ["camera_angle", "composition"]}
        })

    return {
        "continuity_map": style,
        "shots": shots
    }

def generate_project_plan(brief: str, mode: str, num_shots: int) -> ProjectPlan:
    """
    Generates a full project plan from a brief using the simulated Planner Agent.
    """
    project_id = str(uuid.uuid4())
    
    # "Call" the mock LLM
    llm_output = mock_llm_generation(brief, mode, num_shots)
    
    # Parse Continuity Map
    c_data = llm_output["continuity_map"]
    continuity_map = ContinuityMap(
        continuity_id=project_id,
        global_style=c_data["global_style"],
        camera=c_data["camera"],
        lighting=c_data["lighting"],
        composition=c_data["composition"]
    )
    
    # Parse Shots
    shots = [ShotSpec(**s) for s in llm_output["shots"]]
    
    return ProjectPlan(
        project_id=project_id,
        mode=mode,
        brief=brief,
        continuity_map=continuity_map,
        shots=shots
    )
