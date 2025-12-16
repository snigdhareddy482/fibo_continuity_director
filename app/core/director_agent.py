"""
AI Cinematographer / Director Agent

Analyzes scene descriptions and suggests optimal FIBO parameters for:
- Camera settings (lens_mm, FOV, angle)
- Lighting (temperature, key direction, fill/back intensity)
- Color (palette, HDR, bit depth)
- Composition (rule, depth of field)

This module showcases FIBO's unique controllability features.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re


@dataclass
class CameraSuggestion:
    lens_mm: float
    fov_degrees: float
    angle: str
    movement: str
    reason: str


@dataclass
class LightingSuggestion:
    setup: str
    key_direction: str
    fill_intensity: float
    back_intensity: float
    temperature_k: int
    reason: str


@dataclass
class ColorSuggestion:
    palette: str
    hdr: bool
    bit_depth: str
    reason: str


@dataclass
class CompositionSuggestion:
    rule: str
    subject_position: str
    depth_of_field: str
    reason: str


@dataclass
class DirectorSuggestions:
    """Complete set of AI Director suggestions for a scene."""
    camera: CameraSuggestion
    lighting: LightingSuggestion
    color: ColorSuggestion
    composition: CompositionSuggestion
    shot_type: str
    mood: str
    overall_notes: str


# Scene type detection keywords
SCENE_KEYWORDS = {
    "action": ["fight", "chase", "run", "battle", "explosion", "crash", "jump", "fast"],
    "romantic": ["love", "kiss", "embrace", "romantic", "tender", "intimate", "couple"],
    "dramatic": ["tense", "conflict", "confrontation", "emotional", "intense", "dark"],
    "comedy": ["funny", "laugh", "humor", "joke", "silly", "light-hearted"],
    "horror": ["scary", "dark", "shadow", "monster", "fear", "creepy", "haunted"],
    "establishing": ["city", "landscape", "building", "environment", "street", "location"],
    "portrait": ["person", "character", "face", "portrait", "headshot", "close-up"],
    "product": ["product", "item", "object", "display", "showcase", "merchandise"],
}

# Mood detection keywords
MOOD_KEYWORDS = {
    "warm": ["sunset", "golden", "cozy", "warm", "orange", "firelight", "summer"],
    "cold": ["winter", "ice", "cold", "blue", "moonlight", "night", "steel"],
    "neutral": ["daylight", "office", "studio", "clean", "professional"],
    "dramatic": ["contrast", "shadow", "moody", "cinematic", "noir"],
    "dreamy": ["soft", "ethereal", "fantasy", "dream", "magical", "glow"],
}


def detect_scene_type(description: str) -> str:
    """Detect the type of scene from description."""
    desc_lower = description.lower()
    scores = {}
    
    for scene_type, keywords in SCENE_KEYWORDS.items():
        scores[scene_type] = sum(1 for kw in keywords if kw in desc_lower)
    
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"


def detect_mood(description: str) -> str:
    """Detect the mood/atmosphere from description."""
    desc_lower = description.lower()
    scores = {}
    
    for mood, keywords in MOOD_KEYWORDS.items():
        scores[mood] = sum(1 for kw in keywords if kw in desc_lower)
    
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "neutral"


def suggest_camera(scene_type: str, mood: str) -> CameraSuggestion:
    """Generate camera suggestions based on scene type and mood."""
    
    # Camera presets for different scene types
    camera_presets = {
        "action": CameraSuggestion(
            lens_mm=24.0, fov_degrees=70.0, angle="dynamic", movement="tracking",
            reason="Wide lens captures action scope; dynamic angle adds energy"
        ),
        "romantic": CameraSuggestion(
            lens_mm=85.0, fov_degrees=25.0, angle="eye_level", movement="slow_dolly",
            reason="Portrait lens creates intimate bokeh; eye-level connects emotionally"
        ),
        "dramatic": CameraSuggestion(
            lens_mm=35.0, fov_degrees=50.0, angle="low_angle", movement="static",
            reason="Low angle adds power; 35mm balances intimacy with context"
        ),
        "horror": CameraSuggestion(
            lens_mm=18.0, fov_degrees=85.0, angle="dutch", movement="handheld",
            reason="Ultra-wide distorts reality; dutch angle creates unease"
        ),
        "establishing": CameraSuggestion(
            lens_mm=24.0, fov_degrees=70.0, angle="high_angle", movement="crane",
            reason="Wide establishing shot shows environment scale and context"
        ),
        "portrait": CameraSuggestion(
            lens_mm=85.0, fov_degrees=25.0, angle="eye_level", movement="static",
            reason="Classic portrait lens; flattering compression and bokeh"
        ),
        "product": CameraSuggestion(
            lens_mm=100.0, fov_degrees=20.0, angle="slightly_above", movement="static",
            reason="Macro-range lens for crisp detail; slight elevation shows form"
        ),
        "general": CameraSuggestion(
            lens_mm=35.0, fov_degrees=50.0, angle="eye_level", movement="static",
            reason="Versatile 35mm approximates natural human vision"
        ),
    }
    
    return camera_presets.get(scene_type, camera_presets["general"])


def suggest_lighting(scene_type: str, mood: str) -> LightingSuggestion:
    """Generate lighting suggestions based on scene type and mood."""
    
    # Lighting presets combining scene type and mood
    if mood == "warm":
        base = LightingSuggestion(
            setup="golden_hour", key_direction="side", 
            fill_intensity=0.6, back_intensity=0.4, temperature_k=3200,
            reason="Warm temperature (3200K) creates golden hour feel; side key for dimension"
        )
    elif mood == "cold":
        base = LightingSuggestion(
            setup="moonlight", key_direction="top_back",
            fill_intensity=0.3, back_intensity=0.7, temperature_k=6500,
            reason="Cool temperature (6500K) for moonlit/cold atmosphere; rim light emphasis"
        )
    elif mood == "dramatic":
        base = LightingSuggestion(
            setup="chiaroscuro", key_direction="side",
            fill_intensity=0.2, back_intensity=0.5, temperature_k=4500,
            reason="High contrast chiaroscuro; low fill creates dramatic shadows"
        )
    elif mood == "dreamy":
        base = LightingSuggestion(
            setup="soft_diffused", key_direction="front_soft",
            fill_intensity=0.8, back_intensity=0.3, temperature_k=5000,
            reason="Diffused soft light for dreamy/ethereal quality; minimal shadows"
        )
    else:  # neutral
        base = LightingSuggestion(
            setup="studio_soft", key_direction="front_45",
            fill_intensity=0.5, back_intensity=0.3, temperature_k=5500,
            reason="Balanced studio lighting; 5500K daylight standard"
        )
    
    # Adjust for scene type
    if scene_type == "horror":
        base.fill_intensity = 0.1
        base.key_direction = "bottom"
        base.reason = "Uplighting for horror; extreme shadows create fear"
    elif scene_type == "product":
        base.fill_intensity = 0.7
        base.setup = "product_three_point"
        base.reason = "Even product lighting; high fill eliminates harsh shadows"
    
    return base


def suggest_color(scene_type: str, mood: str) -> ColorSuggestion:
    """Generate color palette suggestions."""
    
    palette_map = {
        ("action", "warm"): ("orange_teal", True, "16bit", "Action blockbuster palette; HDR for explosion highlights"),
        ("action", "cold"): ("steel_blue", True, "16bit", "Cold action aesthetic; 16-bit for dynamic range"),
        ("romantic", "warm"): ("rose_gold", True, "16bit", "Romantic warmth; HDR preserves skin tone gradients"),
        ("dramatic", "dramatic"): ("noir_contrast", True, "16bit", "High contrast noir; 16-bit for shadow detail"),
        ("horror", "cold"): ("desaturated_cyan", True, "16bit", "Horror color shift; near-monochrome coldness"),
        ("product", "neutral"): ("clean_white", True, "16bit", "Clean product backdrop; 16-bit for material accuracy"),
        ("establishing", "warm"): ("golden_hour", True, "16bit", "Cinematic golden hour; wide color gamut"),
    }
    
    key = (scene_type, mood)
    if key in palette_map:
        palette, hdr, bit_depth, reason = palette_map[key]
    else:
        palette, hdr, bit_depth, reason = "teal_orange", True, "16bit", "Cinematic teal-orange; industry standard look"
    
    return ColorSuggestion(palette=palette, hdr=hdr, bit_depth=bit_depth, reason=reason)


def suggest_composition(scene_type: str, mood: str) -> CompositionSuggestion:
    """Generate composition suggestions."""
    
    comp_presets = {
        "action": CompositionSuggestion(
            rule="dynamic_diagonal", subject_position="off_center",
            depth_of_field="deep", reason="Diagonal lines add motion; deep DOF shows action context"
        ),
        "romantic": CompositionSuggestion(
            rule="rule_of_thirds", subject_position="thirds_intersection",
            depth_of_field="shallow", reason="Thirds creates balance; shallow DOF isolates couple"
        ),
        "dramatic": CompositionSuggestion(
            rule="golden_ratio", subject_position="golden_point",
            depth_of_field="shallow", reason="Golden ratio for visual power; bokeh for focus"
        ),
        "portrait": CompositionSuggestion(
            rule="centered", subject_position="center",
            depth_of_field="shallow", reason="Centered for portrait impact; creamy background blur"
        ),
        "product": CompositionSuggestion(
            rule="centered", subject_position="center",
            depth_of_field="medium", reason="Product centered for attention; medium DOF shows detail"
        ),
        "establishing": CompositionSuggestion(
            rule="rule_of_thirds", subject_position="lower_third",
            depth_of_field="deep", reason="Thirds for landscape; deep DOF for environment detail"
        ),
    }
    
    return comp_presets.get(scene_type, CompositionSuggestion(
        rule="rule_of_thirds", subject_position="thirds_intersection",
        depth_of_field="medium", reason="Classic rule of thirds for balanced composition"
    ))


def analyze_scene(description: str) -> DirectorSuggestions:
    """
    Main function: Analyze a scene description and return comprehensive 
    FIBO parameter suggestions with reasoning.
    
    Args:
        description: The scene description text
        
    Returns:
        DirectorSuggestions with camera, lighting, color, and composition recommendations
    """
    scene_type = detect_scene_type(description)
    mood = detect_mood(description)
    
    camera = suggest_camera(scene_type, mood)
    lighting = suggest_lighting(scene_type, mood)
    color = suggest_color(scene_type, mood)
    composition = suggest_composition(scene_type, mood)
    
    # Generate overall notes
    notes = f"Scene detected as '{scene_type}' with '{mood}' mood. "
    notes += f"Recommended setup optimizes FIBO's controllable parameters for maximum visual impact."
    
    return DirectorSuggestions(
        camera=camera,
        lighting=lighting,
        color=color,
        composition=composition,
        shot_type=scene_type,
        mood=mood,
        overall_notes=notes
    )


def suggestions_to_fibo_params(suggestions: DirectorSuggestions) -> Dict[str, Any]:
    """Convert DirectorSuggestions to FIBO API parameter format."""
    return {
        "camera": {
            "lens_mm": suggestions.camera.lens_mm,
            "fov_degrees": suggestions.camera.fov_degrees,
            "angle": suggestions.camera.angle,
            "movement": suggestions.camera.movement,
        },
        "lighting": {
            "setup": suggestions.lighting.setup,
            "key_direction": suggestions.lighting.key_direction,
            "fill_intensity": suggestions.lighting.fill_intensity,
            "back_intensity": suggestions.lighting.back_intensity,
            "temperature_k": suggestions.lighting.temperature_k,
        },
        "global_style": {
            "color_palette": suggestions.color.palette,
            "hdr": suggestions.color.hdr,
            "bit_depth": suggestions.color.bit_depth,
        },
        "composition": {
            "rule": suggestions.composition.rule,
            "subject_position": suggestions.composition.subject_position,
            "depth_of_field": suggestions.composition.depth_of_field,
        }
    }


def get_suggestion_explanations(suggestions: DirectorSuggestions) -> Dict[str, str]:
    """Get human-readable explanations for each suggestion category."""
    return {
        "camera": suggestions.camera.reason,
        "lighting": suggestions.lighting.reason,
        "color": suggestions.color.reason,
        "composition": suggestions.composition.reason,
        "overall": suggestions.overall_notes,
    }
