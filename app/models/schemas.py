from pydantic import BaseModel, Field
from typing import Any, Dict, List
from . import config

class ContinuityMap(BaseModel):
    continuity_id: str
    global_style: Dict[str, Any]
    camera: Dict[str, Any]
    lighting: Dict[str, Any]
    composition: Dict[str, Any]

class ShotSpec(BaseModel):
    shot_id: str
    shot_type: str
    description: str
    # New fields for explicit shot roles
    shot_role: str = Field(default="", description="Human-readable shot role label, e.g. 'Wide hero introduction'")
    framing: str = Field(default="medium", description="Framing type: wide, medium, close_up, extreme_closeup")
    camera_angle: str = Field(default="eye_level", description="Camera angle: low_angle, eye_level, high_angle, dutch")
    camera_overrides: Dict[str, Any] = Field(default_factory=dict)
    composition_overrides: Dict[str, Any] = Field(default_factory=dict)
    notes: Dict[str, Any] = Field(default_factory=dict)

class ProjectPlan(BaseModel):
    project_id: str
    mode: str  # "storyboard" or "product"
    brief: str
    continuity_map: ContinuityMap
    shots: List[ShotSpec]

def create_default_continuity_map(continuity_id: str) -> ContinuityMap:
    default_data = config.DEFAULT_CONTINUITY_MAP
    return ContinuityMap(
        continuity_id=continuity_id,
        global_style=default_data["global_style"],
        camera=default_data["camera"],
        lighting=default_data["lighting"],
        composition=default_data["composition"]
    )
