"""
Style DNA Extractor

Extracts visual style from reference images:
- Dominant color palette
- Contrast and saturation levels
- Style tokens for consistent generation

Maps extracted style to FIBO parameters for visual consistency.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import os

# Try to import PIL for image analysis
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


@dataclass
class ColorInfo:
    """Information about a color."""
    rgb: Tuple[int, int, int]
    hex: str
    name: str
    percentage: float


@dataclass 
class StyleDNA:
    """Extracted style information from reference images."""
    dominant_colors: List[ColorInfo]
    color_palette_name: str
    brightness: str  # dark, medium, bright
    contrast: str  # low, medium, high
    saturation: str  # muted, normal, vibrant
    warmth: str  # cool, neutral, warm
    suggested_hdr: bool
    suggested_bit_depth: str
    style_notes: str


# Predefined color palettes
COLOR_PALETTES = {
    "teal_orange": {
        "colors": [(0, 128, 128), (255, 165, 0)],
        "description": "Cinematic teal and orange contrast",
        "warmth": "neutral",
    },
    "noir": {
        "colors": [(20, 20, 20), (80, 80, 80), (200, 200, 200)],
        "description": "High contrast black and white",
        "warmth": "cool",
    },
    "golden_hour": {
        "colors": [(255, 200, 100), (255, 150, 50), (200, 100, 50)],
        "description": "Warm golden sunset tones",
        "warmth": "warm",
    },
    "moody_blue": {
        "colors": [(30, 60, 100), (50, 80, 130), (100, 130, 170)],
        "description": "Cool blue atmospheric tones",
        "warmth": "cool",
    },
    "forest_green": {
        "colors": [(34, 85, 51), (60, 120, 80), (100, 160, 100)],
        "description": "Natural forest greens",
        "warmth": "neutral",
    },
    "pastel_dream": {
        "colors": [(255, 200, 200), (200, 220, 255), (255, 255, 200)],
        "description": "Soft pastel colors",
        "warmth": "neutral",
    },
    "neon_cyber": {
        "colors": [(255, 0, 255), (0, 255, 255), (255, 0, 100)],
        "description": "Vibrant neon cyberpunk",
        "warmth": "cool",
    },
    "earthy_natural": {
        "colors": [(139, 90, 43), (160, 120, 70), (200, 180, 140)],
        "description": "Natural earth tones",
        "warmth": "warm",
    },
}


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB to hex color code."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def get_color_name(rgb: Tuple[int, int, int]) -> str:
    """Get approximate color name from RGB."""
    r, g, b = rgb
    
    # Simple color naming based on RGB
    if r > 200 and g > 200 and b > 200:
        return "white"
    elif r < 50 and g < 50 and b < 50:
        return "black"
    elif r > g and r > b:
        if g > 150:
            return "yellow"
        elif b > 150:
            return "magenta"
        else:
            return "red"
    elif g > r and g > b:
        if r > 150:
            return "yellow"
        elif b > 150:
            return "cyan"
        else:
            return "green"
    elif b > r and b > g:
        if r > 150:
            return "magenta"
        elif g > 150:
            return "cyan"
        else:
            return "blue"
    else:
        return "gray"


def analyze_brightness(colors: List[Tuple[int, int, int]]) -> str:
    """Analyze overall brightness from colors."""
    if not colors:
        return "medium"
    
    avg_brightness = sum(sum(c) / 3 for c in colors) / len(colors)
    
    if avg_brightness > 180:
        return "bright"
    elif avg_brightness < 80:
        return "dark"
    else:
        return "medium"


def analyze_saturation(colors: List[Tuple[int, int, int]]) -> str:
    """Analyze color saturation."""
    if not colors:
        return "normal"
    
    saturations = []
    for r, g, b in colors:
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if max_c > 0:
            sat = (max_c - min_c) / max_c
            saturations.append(sat)
    
    if not saturations:
        return "normal"
    
    avg_sat = sum(saturations) / len(saturations)
    
    if avg_sat > 0.6:
        return "vibrant"
    elif avg_sat < 0.25:
        return "muted"
    else:
        return "normal"


def analyze_warmth(colors: List[Tuple[int, int, int]]) -> str:
    """Analyze color temperature/warmth."""
    if not colors:
        return "neutral"
    
    warm_score = 0
    for r, g, b in colors:
        # More red/yellow = warmer, more blue = cooler
        warm_score += (r - b) / 255
    
    avg_warmth = warm_score / len(colors)
    
    if avg_warmth > 0.2:
        return "warm"
    elif avg_warmth < -0.2:
        return "cool"
    else:
        return "neutral"


def analyze_contrast(colors: List[Tuple[int, int, int]]) -> str:
    """Analyze contrast level from colors."""
    if len(colors) < 2:
        return "medium"
    
    brightnesses = [sum(c) / 3 for c in colors]
    contrast_range = max(brightnesses) - min(brightnesses)
    
    if contrast_range > 150:
        return "high"
    elif contrast_range < 50:
        return "low"
    else:
        return "medium"


def match_to_palette(colors: List[Tuple[int, int, int]]) -> str:
    """Match extracted colors to a predefined palette."""
    if not colors:
        return "teal_orange"  # Default
    
    warmth = analyze_warmth(colors)
    saturation = analyze_saturation(colors)
    brightness = analyze_brightness(colors)
    
    # Match based on characteristics
    if saturation == "vibrant" and brightness == "dark":
        return "neon_cyber"
    elif warmth == "warm" and saturation == "vibrant":
        return "golden_hour"
    elif warmth == "cool" and brightness == "dark":
        return "moody_blue"
    elif warmth == "cool" and saturation == "muted":
        return "noir"
    elif warmth == "warm" and saturation == "muted":
        return "earthy_natural"
    elif brightness == "bright" and saturation == "muted":
        return "pastel_dream"
    else:
        return "teal_orange"


def extract_style_from_colors(colors: List[Tuple[int, int, int]], source: str = "manual") -> StyleDNA:
    """
    Extract style DNA from a list of colors.
    
    Args:
        colors: List of RGB color tuples
        source: Where the colors came from
        
    Returns:
        StyleDNA with comprehensive style information
    """
    # Analyze color properties
    brightness = analyze_brightness(colors)
    contrast = analyze_contrast(colors)
    saturation = analyze_saturation(colors)
    warmth = analyze_warmth(colors)
    
    # Match to palette
    palette_name = match_to_palette(colors)
    
    # Build color info list
    color_infos = []
    for i, rgb in enumerate(colors[:5]):  # Top 5 colors
        color_infos.append(ColorInfo(
            rgb=rgb,
            hex=rgb_to_hex(rgb),
            name=get_color_name(rgb),
            percentage=100 / len(colors[:5])  # Simplified
        ))
    
    # Determine HDR recommendation
    suggested_hdr = contrast == "high" or saturation == "vibrant"
    
    # Build style notes
    notes_parts = [
        f"Style from {source}.",
        f"Palette: {palette_name}.",
        f"Mood: {brightness} lighting with {contrast} contrast.",
    ]
    if warmth != "neutral":
        notes_parts.append(f"Color temperature leans {warmth}.")
    
    return StyleDNA(
        dominant_colors=color_infos,
        color_palette_name=palette_name,
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
        warmth=warmth,
        suggested_hdr=suggested_hdr,
        suggested_bit_depth="16bit" if suggested_hdr else "8bit",
        style_notes=" ".join(notes_parts)
    )


def extract_style_from_image(image_path: str) -> Optional[StyleDNA]:
    """
    Extract style DNA from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        StyleDNA or None if extraction fails
    """
    if not HAS_PIL:
        # Return a default style if PIL not available
        return extract_style_from_colors(
            [(139, 61, 255), (91, 31, 184), (200, 180, 255)],
            source="default (PIL not available)"
        )
    
    if not os.path.exists(image_path):
        return None
    
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        
        # Resize for faster processing
        img.thumbnail((100, 100))
        
        # Get colors (simplified - just sample pixels)
        pixels = list(img.getdata())
        
        # Simple color clustering (take sample of pixels)
        sample_colors = pixels[::max(1, len(pixels) // 10)][:20]
        
        # Average similar colors
        unique_colors = []
        for color in sample_colors:
            is_unique = True
            for existing in unique_colors:
                diff = sum(abs(a - b) for a, b in zip(color, existing))
                if diff < 30:  # Similar color threshold
                    is_unique = False
                    break
            if is_unique:
                unique_colors.append(color)
        
        return extract_style_from_colors(unique_colors[:5], source=os.path.basename(image_path))
        
    except Exception as e:
        return None


def style_to_fibo_params(style: StyleDNA) -> Dict[str, Any]:
    """
    Convert StyleDNA to FIBO API parameters.
    
    Args:
        style: Extracted style DNA
        
    Returns:
        Dictionary of FIBO parameters
    """
    # Map warmth to color temperature
    temp_map = {
        "warm": 3500,
        "neutral": 5500,
        "cool": 6500,
    }
    
    # Map contrast to fill intensity (inverse relationship)
    fill_map = {
        "high": 0.3,
        "medium": 0.5,
        "low": 0.7,
    }
    
    return {
        "global_style": {
            "color_palette": style.color_palette_name,
            "hdr": style.suggested_hdr,
            "bit_depth": style.suggested_bit_depth,
        },
        "lighting": {
            "temperature_k": temp_map.get(style.warmth, 5500),
            "fill_intensity": fill_map.get(style.contrast, 0.5),
        },
        "notes": style.style_notes,
    }


def get_palette_preview(palette_name: str) -> List[str]:
    """Get hex colors for a palette preview."""
    palette = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["teal_orange"])
    return [rgb_to_hex(c) for c in palette["colors"]]
