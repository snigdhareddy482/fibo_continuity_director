"""
Unit tests for the helpers module.
"""
import pytest
import os
import tempfile
import json
from PIL import Image

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.helpers import (
    create_storyboard_grid,
    safe_project_id_from_brief,
    save_project,
    load_project,
    list_saved_projects
)


def create_test_images(count: int = 3) -> list:
    """Create temporary test images."""
    paths = []
    for i in range(count):
        img = Image.new('RGB', (100, 100), (i * 50, i * 50, i * 50))
        temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp.name)
        paths.append(temp.name)
    return paths


class TestCreateStoryboardGrid:
    def test_creates_grid(self, tmp_path):
        """Test grid creation from images."""
        paths = create_test_images(4)
        output = str(tmp_path / "grid.png")
        
        try:
            result = create_storyboard_grid(paths, output)
            assert result == output
            assert os.path.exists(output)
            
            # Check it's a valid image
            img = Image.open(output)
            assert img.size[0] > 0
        finally:
            for p in paths:
                os.unlink(p)
    
    def test_empty_list(self, tmp_path):
        """Empty list should return empty string."""
        output = str(tmp_path / "grid.png")
        result = create_storyboard_grid([], output)
        assert result == ""


class TestSafeProjectId:
    def test_basic(self):
        """Test basic brief to ID conversion."""
        result = safe_project_id_from_brief("A cyberpunk scene")
        assert "a_cyberpunk_scene" in result
        assert len(result) > 15  # includes UUID suffix
    
    def test_empty(self):
        """Empty brief should use 'project' prefix."""
        result = safe_project_id_from_brief("")
        assert result.startswith("project_")


class TestSaveLoadProject:
    def test_save_and_load(self, tmp_path):
        """Test saving and loading a project."""
        project_dir = str(tmp_path / "test_project")
        
        plan = {"project_id": "test", "brief": "Test brief"}
        outputs = [{"shot_id": "shot_001", "image_path": "/fake/path.png"}]
        
        # Save
        save_path = save_project(project_dir, "Test Project", plan, outputs)
        assert os.path.exists(save_path)
        
        # Load
        loaded = load_project(project_dir)
        assert loaded is not None
        assert loaded["project_name"] == "Test Project"
        assert loaded["plan"]["brief"] == "Test brief"
    
    def test_load_missing(self, tmp_path):
        """Loading from non-existent dir should return None."""
        result = load_project(str(tmp_path / "nonexistent"))
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
