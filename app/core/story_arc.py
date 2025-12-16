"""
Story Arc Generator

Generates narrative structure from themes/briefs:
- 3-act structure (Setup, Confrontation, Resolution)
- Story beats with visual descriptions
- Maps emotions to camera angles and lighting

This module adds creative value by automating story structure.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ActType(Enum):
    SETUP = "setup"
    CONFRONTATION = "confrontation"
    RESOLUTION = "resolution"


class EmotionType(Enum):
    NEUTRAL = "neutral"
    HOPEFUL = "hopeful"
    TENSE = "tense"
    TRIUMPHANT = "triumphant"
    MELANCHOLY = "melancholy"
    FEARFUL = "fearful"
    JOYFUL = "joyful"
    ANGRY = "angry"


@dataclass
class StoryBeat:
    """A single moment in the story."""
    beat_id: str
    act: ActType
    title: str
    description: str
    emotion: EmotionType
    suggested_shot_type: str
    suggested_camera_angle: str
    suggested_lighting_mood: str
    notes: str = ""


@dataclass
class StoryArc:
    """Complete 3-act story structure."""
    theme: str
    num_beats: int
    setup_beats: List[StoryBeat] = field(default_factory=list)
    confrontation_beats: List[StoryBeat] = field(default_factory=list)
    resolution_beats: List[StoryBeat] = field(default_factory=list)
    
    @property
    def all_beats(self) -> List[StoryBeat]:
        return self.setup_beats + self.confrontation_beats + self.resolution_beats


# Theme to story structure mapping
THEME_TEMPLATES = {
    "hero's journey": {
        "setup": [
            ("The Ordinary World", "Character in their normal environment", EmotionType.NEUTRAL, "wide_establishing"),
            ("Call to Adventure", "Something disrupts the status quo", EmotionType.HOPEFUL, "medium_character"),
        ],
        "confrontation": [
            ("Crossing the Threshold", "Character commits to the journey", EmotionType.TENSE, "low_angle_hero"),
            ("Tests and Allies", "Challenges and new relationships", EmotionType.HOPEFUL, "over_the_shoulder"),
            ("The Ordeal", "Major crisis or confrontation", EmotionType.FEARFUL, "dutch_angle"),
        ],
        "resolution": [
            ("The Reward", "Character gains what they sought", EmotionType.TRIUMPHANT, "close_up"),
            ("The Return", "Character returns transformed", EmotionType.JOYFUL, "wide_establishing"),
        ],
    },
    "rise and fall": {
        "setup": [
            ("Humble Beginnings", "Start from nothing", EmotionType.NEUTRAL, "wide_establishing"),
            ("First Success", "Initial breakthrough", EmotionType.HOPEFUL, "medium_character"),
        ],
        "confrontation": [
            ("Growing Ambition", "Reaching for more", EmotionType.HOPEFUL, "low_angle_hero"),
            ("Peak of Power", "Highest point", EmotionType.TRIUMPHANT, "extreme_closeup"),
            ("The Fall Begins", "Cracks appear", EmotionType.TENSE, "dutch_angle"),
        ],
        "resolution": [
            ("Rock Bottom", "Complete collapse", EmotionType.MELANCHOLY, "high_angle_context"),
            ("Reflection", "Finding meaning", EmotionType.NEUTRAL, "close_up"),
        ],
    },
    "love story": {
        "setup": [
            ("Two Worlds", "Characters in separate lives", EmotionType.NEUTRAL, "wide_establishing"),
            ("The Meeting", "First encounter", EmotionType.HOPEFUL, "medium_character"),
        ],
        "confrontation": [
            ("Growing Connection", "Relationship develops", EmotionType.JOYFUL, "over_the_shoulder"),
            ("The Obstacle", "Something threatens the bond", EmotionType.TENSE, "close_up"),
            ("Separation", "Time apart", EmotionType.MELANCHOLY, "wide_establishing"),
        ],
        "resolution": [
            ("Realization", "Understanding true feelings", EmotionType.HOPEFUL, "close_up"),
            ("Reunion", "Coming back together", EmotionType.JOYFUL, "medium_character"),
        ],
    },
    "mystery": {
        "setup": [
            ("The Discovery", "Something unusual found", EmotionType.NEUTRAL, "wide_establishing"),
            ("First Clue", "Initial investigation", EmotionType.HOPEFUL, "close_up"),
        ],
        "confrontation": [
            ("Deep Dive", "Uncovering more", EmotionType.TENSE, "over_the_shoulder"),
            ("Red Herring", "False lead", EmotionType.FEARFUL, "dutch_angle"),
            ("The Reveal", "Truth begins to emerge", EmotionType.TENSE, "extreme_closeup"),
        ],
        "resolution": [
            ("Confrontation", "Facing the truth", EmotionType.TENSE, "low_angle_hero"),
            ("Resolution", "Mystery solved", EmotionType.TRIUMPHANT, "medium_character"),
        ],
    },
    "product showcase": {
        "setup": [
            ("The Problem", "Pain point visualization", EmotionType.NEUTRAL, "wide_establishing"),
            ("Discovery", "Finding the product", EmotionType.HOPEFUL, "medium_character"),
        ],
        "confrontation": [
            ("Features", "Product capabilities", EmotionType.NEUTRAL, "close_up"),
            ("In Action", "Product being used", EmotionType.JOYFUL, "over_the_shoulder"),
            ("Results", "Transformation shown", EmotionType.TRIUMPHANT, "medium_character"),
        ],
        "resolution": [
            ("Hero Shot", "Product in glory", EmotionType.TRIUMPHANT, "low_angle_hero"),
            ("Call to Action", "Final appeal", EmotionType.HOPEFUL, "close_up"),
        ],
    },
}

# Emotion to visual mapping
EMOTION_VISUALS = {
    EmotionType.NEUTRAL: {"angle": "eye_level", "lighting": "neutral", "color_temp": 5500},
    EmotionType.HOPEFUL: {"angle": "slightly_up", "lighting": "warm", "color_temp": 4500},
    EmotionType.TENSE: {"angle": "low_angle", "lighting": "dramatic", "color_temp": 4000},
    EmotionType.TRIUMPHANT: {"angle": "low_angle", "lighting": "golden", "color_temp": 3500},
    EmotionType.MELANCHOLY: {"angle": "high_angle", "lighting": "cold", "color_temp": 6500},
    EmotionType.FEARFUL: {"angle": "dutch", "lighting": "harsh_shadow", "color_temp": 6000},
    EmotionType.JOYFUL: {"angle": "eye_level", "lighting": "bright_warm", "color_temp": 4000},
    EmotionType.ANGRY: {"angle": "low_angle", "lighting": "high_contrast", "color_temp": 5000},
}


def detect_theme(brief: str) -> str:
    """Detect story theme from brief description."""
    brief_lower = brief.lower()
    
    theme_keywords = {
        "hero's journey": ["hero", "journey", "adventure", "quest", "destiny", "overcome"],
        "rise and fall": ["rise", "fall", "ambition", "power", "corruption", "greed"],
        "love story": ["love", "romance", "heart", "relationship", "couple", "together"],
        "mystery": ["mystery", "clue", "detective", "secret", "hidden", "discover"],
        "product showcase": ["product", "feature", "benefit", "solution", "demo", "showcase"],
    }
    
    scores = {}
    for theme, keywords in theme_keywords.items():
        scores[theme] = sum(1 for kw in keywords if kw in brief_lower)
    
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "hero's journey"  # Default


def generate_story_arc(theme: str, num_shots: int, brief: str = "") -> StoryArc:
    """
    Generate a complete story arc with beats.
    
    Args:
        theme: Story theme/type
        num_shots: Total number of shots to generate
        brief: Optional brief to customize beats
        
    Returns:
        StoryArc with structured beats
    """
    # Get template or use default
    template = THEME_TEMPLATES.get(theme, THEME_TEMPLATES["hero's journey"])
    
    # Calculate beat distribution across acts (roughly 25% - 50% - 25%)
    setup_count = max(1, num_shots // 4)
    resolution_count = max(1, num_shots // 4)
    confrontation_count = num_shots - setup_count - resolution_count
    
    arc = StoryArc(theme=theme, num_beats=num_shots)
    
    # Generate setup beats
    for i in range(setup_count):
        template_idx = i % len(template["setup"])
        title, desc, emotion, shot_type = template["setup"][template_idx]
        
        visuals = EMOTION_VISUALS[emotion]
        
        beat = StoryBeat(
            beat_id=f"beat_{i+1:02d}",
            act=ActType.SETUP,
            title=title,
            description=f"{desc}. {brief}" if brief else desc,
            emotion=emotion,
            suggested_shot_type=shot_type,
            suggested_camera_angle=visuals["angle"],
            suggested_lighting_mood=visuals["lighting"],
            notes=f"Color temp: {visuals['color_temp']}K"
        )
        arc.setup_beats.append(beat)
    
    # Generate confrontation beats
    for i in range(confrontation_count):
        template_idx = i % len(template["confrontation"])
        title, desc, emotion, shot_type = template["confrontation"][template_idx]
        
        visuals = EMOTION_VISUALS[emotion]
        
        beat = StoryBeat(
            beat_id=f"beat_{setup_count + i + 1:02d}",
            act=ActType.CONFRONTATION,
            title=title,
            description=f"{desc}. {brief}" if brief else desc,
            emotion=emotion,
            suggested_shot_type=shot_type,
            suggested_camera_angle=visuals["angle"],
            suggested_lighting_mood=visuals["lighting"],
            notes=f"Color temp: {visuals['color_temp']}K"
        )
        arc.confrontation_beats.append(beat)
    
    # Generate resolution beats
    for i in range(resolution_count):
        template_idx = i % len(template["resolution"])
        title, desc, emotion, shot_type = template["resolution"][template_idx]
        
        visuals = EMOTION_VISUALS[emotion]
        
        beat = StoryBeat(
            beat_id=f"beat_{setup_count + confrontation_count + i + 1:02d}",
            act=ActType.RESOLUTION,
            title=title,
            description=f"{desc}. {brief}" if brief else desc,
            emotion=emotion,
            suggested_shot_type=shot_type,
            suggested_camera_angle=visuals["angle"],
            suggested_lighting_mood=visuals["lighting"],
            notes=f"Color temp: {visuals['color_temp']}K"
        )
        arc.resolution_beats.append(beat)
    
    return arc


def arc_to_shot_specs(arc: StoryArc) -> List[Dict[str, Any]]:
    """Convert story arc beats to shot specification format."""
    shots = []
    
    for beat in arc.all_beats:
        shots.append({
            "shot_id": beat.beat_id.replace("beat", "shot"),
            "shot_type": beat.suggested_shot_type,
            "description": beat.description,
            "shot_role": beat.title,
            "framing": _shot_type_to_framing(beat.suggested_shot_type),
            "camera_angle": beat.suggested_camera_angle,
            "emotion": beat.emotion.value,
            "act": beat.act.value,
            "notes": beat.notes,
        })
    
    return shots


def _shot_type_to_framing(shot_type: str) -> str:
    """Convert shot type to framing category."""
    framing_map = {
        "wide_establishing": "wide",
        "medium_character": "medium",
        "close_up": "close_up",
        "extreme_closeup": "extreme_closeup",
        "over_the_shoulder": "medium",
        "low_angle_hero": "medium",
        "high_angle_context": "wide",
        "dutch_angle": "medium",
    }
    return framing_map.get(shot_type, "medium")


def get_arc_summary(arc: StoryArc) -> Dict[str, Any]:
    """Get a summary of the story arc for display."""
    return {
        "theme": arc.theme,
        "total_beats": arc.num_beats,
        "structure": {
            "setup": len(arc.setup_beats),
            "confrontation": len(arc.confrontation_beats),
            "resolution": len(arc.resolution_beats),
        },
        "emotional_journey": [beat.emotion.value for beat in arc.all_beats],
        "shot_types": [beat.suggested_shot_type for beat in arc.all_beats],
    }
