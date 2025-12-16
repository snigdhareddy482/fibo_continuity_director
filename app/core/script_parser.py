"""
Script Parser

Parses screenplay/script format and extracts:
- Scene headings (INT./EXT., location, time)
- Characters and dialogue
- Action descriptions
- Auto-generates shot list with FIBO parameters

Professional workflow feature for converting scripts to storyboards.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class SceneHeading:
    """Parsed scene heading."""
    int_ext: str  # INT or EXT
    location: str
    time_of_day: str
    raw_text: str


@dataclass
class DialogueLine:
    """A line of dialogue."""
    character: str
    line: str
    parenthetical: Optional[str] = None


@dataclass
class ActionLine:
    """An action/description line."""
    text: str
    suggested_shot: Optional[str] = None


@dataclass
class ScriptScene:
    """A complete scene from the script."""
    scene_number: int
    heading: SceneHeading
    actions: List[ActionLine] = field(default_factory=list)
    dialogue: List[DialogueLine] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    
    @property
    def description(self) -> str:
        """Get a combined description for image generation."""
        parts = [self.heading.location]
        if self.actions:
            parts.append(self.actions[0].text[:200])  # First action line
        if self.characters:
            parts.append(f"Characters: {', '.join(self.characters)}")
        return ". ".join(parts)


# Regex patterns for screenplay format
SCENE_HEADING_PATTERN = re.compile(
    r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)\s*(.+?)(?:\s*[-–—]\s*|\s+)(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|LATER|CONTINUOUS|SAME)?\.?\s*$',
    re.IGNORECASE | re.MULTILINE
)

CHARACTER_CUE_PATTERN = re.compile(
    r'^([A-Z][A-Z\s\.\'\-]+)(?:\s*\(([^)]+)\))?\s*$',
    re.MULTILINE
)

PARENTHETICAL_PATTERN = re.compile(r'^\(([^)]+)\)$')

# Time of day to lighting mapping
TIME_LIGHTING = {
    "DAY": {"temperature_k": 5500, "intensity": 1.0, "mood": "bright"},
    "NIGHT": {"temperature_k": 4000, "intensity": 0.3, "mood": "dark"},
    "DAWN": {"temperature_k": 3500, "intensity": 0.6, "mood": "warm_soft"},
    "DUSK": {"temperature_k": 3200, "intensity": 0.5, "mood": "golden"},
    "MORNING": {"temperature_k": 5000, "intensity": 0.8, "mood": "fresh"},
    "EVENING": {"temperature_k": 4000, "intensity": 0.6, "mood": "warm"},
}

# Location to shot type suggestions
LOCATION_SHOTS = {
    "office": ["medium_character", "over_the_shoulder", "wide_establishing"],
    "street": ["wide_establishing", "tracking", "medium_character"],
    "bedroom": ["close_up", "medium_character", "intimate"],
    "restaurant": ["two_shot", "over_the_shoulder", "wide_establishing"],
    "car": ["close_up", "over_the_shoulder", "dashboard"],
    "forest": ["wide_establishing", "tracking", "low_angle_hero"],
    "beach": ["wide_establishing", "silhouette", "close_up"],
    "rooftop": ["wide_establishing", "dramatic", "low_angle_hero"],
}


def parse_script(script_text: str) -> List[ScriptScene]:
    """
    Parse a screenplay text into structured scenes.
    
    Args:
        script_text: Raw screenplay text
        
    Returns:
        List of ScriptScene objects
    """
    scenes = []
    current_scene = None
    lines = script_text.strip().split('\n')
    
    i = 0
    scene_num = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check for scene heading
        heading_match = SCENE_HEADING_PATTERN.match(line)
        if heading_match:
            # Save previous scene if exists
            if current_scene:
                scenes.append(current_scene)
            
            scene_num += 1
            int_ext = heading_match.group(1).upper().rstrip('.')
            location = heading_match.group(2).strip()
            time_of_day = heading_match.group(3) or "DAY"
            
            current_scene = ScriptScene(
                scene_number=scene_num,
                heading=SceneHeading(
                    int_ext=int_ext,
                    location=location,
                    time_of_day=time_of_day.upper(),
                    raw_text=line
                )
            )
            i += 1
            continue
        
        # If no current scene, create a default one
        if not current_scene:
            scene_num += 1
            current_scene = ScriptScene(
                scene_number=scene_num,
                heading=SceneHeading(
                    int_ext="INT",
                    location="UNKNOWN",
                    time_of_day="DAY",
                    raw_text=""
                )
            )
        
        # Check for character cue (all caps, possibly with parenthetical)
        char_match = CHARACTER_CUE_PATTERN.match(line)
        if char_match and len(line) < 40:  # Character names are typically short
            character = char_match.group(1).strip()
            # Skip common non-character words
            if character not in ['THE', 'AND', 'BUT', 'ACTION', 'CUT TO', 'FADE IN', 'FADE OUT']:
                if character not in current_scene.characters:
                    current_scene.characters.append(character)
                
                # Look for dialogue on next lines
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        break
                    
                    # Check for parenthetical
                    paren_match = PARENTHETICAL_PATTERN.match(next_line)
                    if paren_match:
                        i += 1
                        continue
                    
                    # Check if it's dialogue (indented or regular text after character)
                    if not SCENE_HEADING_PATTERN.match(next_line) and not CHARACTER_CUE_PATTERN.match(next_line):
                        current_scene.dialogue.append(DialogueLine(
                            character=character,
                            line=next_line
                        ))
                        i += 1
                    else:
                        break
                continue
        
        # Otherwise it's action/description
        current_scene.actions.append(ActionLine(
            text=line,
            suggested_shot=_suggest_shot_from_action(line)
        ))
        i += 1
    
    # Don't forget the last scene
    if current_scene:
        scenes.append(current_scene)
    
    return scenes


def _suggest_shot_from_action(action_text: str) -> str:
    """Suggest a shot type based on action description."""
    action_lower = action_text.lower()
    
    # Shot type keywords
    shot_keywords = {
        "close_up": ["face", "eyes", "hand", "detail", "looks at", "stares"],
        "wide_establishing": ["enters", "walks into", "arrives", "exterior", "landscape"],
        "medium_character": ["stands", "sits", "talks", "speaks", "responds"],
        "over_the_shoulder": ["faces", "confronts", "conversation", "dialogue"],
        "tracking": ["runs", "chases", "follows", "moves through", "walks along"],
        "low_angle_hero": ["rises", "stands tall", "powerful", "dominates"],
        "high_angle_context": ["looks down", "from above", "aerial", "overlook"],
    }
    
    for shot_type, keywords in shot_keywords.items():
        if any(kw in action_lower for kw in keywords):
            return shot_type
    
    return "medium_character"  # Default


def scenes_to_shots(scenes: List[ScriptScene], max_shots_per_scene: int = 3) -> List[Dict[str, Any]]:
    """
    Convert parsed scenes to shot specifications for FIBO.
    
    Args:
        scenes: List of parsed ScriptScene objects
        max_shots_per_scene: Maximum shots to generate per scene
        
    Returns:
        List of shot specifications
    """
    shots = []
    shot_num = 0
    
    for scene in scenes:
        # Get lighting based on time of day
        lighting = TIME_LIGHTING.get(scene.heading.time_of_day, TIME_LIGHTING["DAY"])
        
        # Get location-based shot suggestions
        location_lower = scene.heading.location.lower()
        suggested_shots = ["wide_establishing", "medium_character", "close_up"]
        for loc_key, loc_shots in LOCATION_SHOTS.items():
            if loc_key in location_lower:
                suggested_shots = loc_shots
                break
        
        # Generate shots for this scene
        num_shots = min(max_shots_per_scene, len(suggested_shots))
        
        for i in range(num_shots):
            shot_num += 1
            shot_type = suggested_shots[i % len(suggested_shots)]
            
            # Build description
            desc_parts = [
                f"{scene.heading.int_ext}. {scene.heading.location}.",
                f"Time: {scene.heading.time_of_day}.",
            ]
            
            if scene.actions and i < len(scene.actions):
                desc_parts.append(scene.actions[i].text)
            elif scene.actions:
                desc_parts.append(scene.actions[0].text)
            
            if scene.characters:
                desc_parts.append(f"Featuring: {', '.join(scene.characters[:2])}")
            
            shots.append({
                "shot_id": f"shot_{shot_num:03d}",
                "scene_number": scene.scene_number,
                "shot_type": shot_type,
                "description": " ".join(desc_parts),
                "location": scene.heading.location,
                "time_of_day": scene.heading.time_of_day,
                "int_ext": scene.heading.int_ext,
                "lighting": lighting,
                "characters": scene.characters[:3],  # Limit characters
            })
    
    return shots


def get_script_summary(scenes: List[ScriptScene]) -> Dict[str, Any]:
    """Get a summary of the parsed script."""
    all_characters = set()
    all_locations = set()
    
    for scene in scenes:
        all_characters.update(scene.characters)
        all_locations.add(scene.heading.location)
    
    return {
        "total_scenes": len(scenes),
        "characters": list(all_characters),
        "locations": list(all_locations),
        "int_ext_breakdown": {
            "interior": sum(1 for s in scenes if s.heading.int_ext == "INT"),
            "exterior": sum(1 for s in scenes if s.heading.int_ext == "EXT"),
        }
    }


# Example screenplay for testing
SAMPLE_SCREENPLAY = """
INT. COFFEE SHOP - DAY

SARAH, 30s, sits alone at a corner table, nursing a cold coffee.

The door chimes. MICHAEL, 35, enters, scanning the room.

MICHAEL
(nervous)
Sarah?

SARAH
You came.

They share an awkward silence.

EXT. CITY STREET - NIGHT

Sarah walks alone under streetlights.

She pauses at a corner, looking back.

INT. MICHAEL'S APARTMENT - EVENING

Michael stares at his phone, a message half-typed.

He deletes it. Types again. Deletes.
"""
