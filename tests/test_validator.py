"""
Unit tests for the validator module.
"""
import pytest
import os
import tempfile
from PIL import Image
import numpy as np

# Add parent to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.validator import get_avg_color, color_distance, validate_continuity


def create_test_image(color: tuple, size: tuple = (64, 64)) -> str:
    """Helper to create a temporary test image with a solid color."""
    img = Image.new('RGB', size, color)
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name)
    return temp_file.name


class TestGetAvgColor:
    def test_solid_red(self):
        """Test average color of solid red image."""
        path = create_test_image((255, 0, 0))
        try:
            h, s, v = get_avg_color(path)
            # Red in HSV should have H close to 0 or 1
            assert s > 0.8  # Saturated
            assert v > 0.8  # Bright
        finally:
            os.unlink(path)
    
    def test_solid_gray(self):
        """Test average color of gray image."""
        path = create_test_image((128, 128, 128))
        try:
            h, s, v = get_avg_color(path)
            assert s < 0.1  # Gray should have low saturation
        finally:
            os.unlink(path)
    
    def test_missing_file(self):
        """Test graceful handling of missing file."""
        result = get_avg_color("/nonexistent/path.png")
        assert result == (0.0, 0.0, 0.0)


class TestColorDistance:
    def test_identical_colors(self):
        """Distance between identical colors should be 0."""
        c1 = (0.5, 0.5, 0.5)
        assert color_distance(c1, c1) == 0.0
    
    def test_different_colors(self):
        """Distance between different colors should be positive."""
        c1 = (0.0, 0.0, 0.0)
        c2 = (1.0, 1.0, 1.0)
        assert color_distance(c1, c2) > 0


class TestValidateContinuity:
    def test_empty_outputs(self):
        """Empty list should return empty list."""
        result = validate_continuity([])
        assert result == []
    
    def test_single_output(self):
        """Single output should validate against itself."""
        path = create_test_image((100, 100, 100))
        try:
            outputs = [{"shot_id": "shot_001", "image_path": path}]
            result = validate_continuity(outputs)
            assert len(result) == 1
            assert "continuity_score" in result[0]
        finally:
            os.unlink(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
