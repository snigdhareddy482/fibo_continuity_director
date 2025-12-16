import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load env vars from .env if present
load_dotenv()

# Environment Variables
FIBO_API_URL = os.getenv("FIBO_API_URL", "https://engine.prod.bria-api.com/v2/image/generate")
FIBO_API_KEY = os.getenv("FIBO_API_KEY")

# Paths
OUTPUT_DIR = "outputs"

DEFAULT_NEGATIVE_PROMPT = "blurry, low quality, distortion, watermark, text, signature, bad anatomy, deformed"

# Default Continuity Map
DEFAULT_CONTINUITY_MAP: Dict[str, Any] = {
    "global_style": {
        "look": "cinematic",
        "color_palette": "warm_muted",
        "hdr": True,
        "bit_depth": "16bit"
    },
    "camera": {
        "lens_mm": 50.0,
        "fov_degrees": 45.0,
        "height_m": 1.6,
        "angle": "eye_level",
        "movement": "static"
    },
    "lighting": {
        "setup": "three_point",
        "key_direction": "front_left",
        "fill_intensity": 0.6,
        "back_intensity": 0.4,
        "temperature_k": 5200
    },
    "composition": {
        "rule": "rule_of_thirds",
        "subject_position": "center_left",
        "depth_of_field": "shallow"
    }
}

# Validator Thresholds
COLOR_TOLERANCE = 0.15
BRIGHTNESS_TOLERANCE = 0.25

def ensure_output_dir() -> None:
    """Creates the OUTPUT_DIR if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
