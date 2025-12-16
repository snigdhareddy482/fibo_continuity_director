# FIBO Continuity Director - Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-12-12

### Added
- **Character Consistency**: First shot now serves as reference for subsequent shots
- **Character Reference Upload**: Optional upload of character reference image
- **Project Persistence**: Auto-save after generation + manual save button
- **Load Previous Projects**: Dropdown in sidebar to load saved projects
- **Image Zoom**: Expandable full-size image view for each shot
- **Shot Role Labels**: Prominent display of shot roles (e.g., "Wide hero introduction")
- **Visual Badges**: Framing, camera angle, and composition badges
- **Continuity Indicators**: Shows what's kept consistent vs. varied
- **Per-Shot Edit Controls**: Change camera angle and composition per shot
- **Better Error Messages**: User-friendly error translations

### Fixed
- Corrupted `requirements.txt` (null bytes removed)
- Wrong import in `scripts/verify.py` (BRIA_BASE_URL → FIBO_API_URL)
- Pydantic field assignment error in shot edit controls

### Technical
- Added `.gitignore` to protect sensitive files
- Created `tests/` directory with validator and helpers tests
- Added `save_project`, `load_project`, `list_saved_projects` to helpers

## [1.0.0] - 2024-12-12

### Initial Release
- Text-to-image generation via Bria FIBO API
- Multi-shot storyboard planning
- Continuity controls (camera, lighting, palette)
- Shot refinement (image-to-image)
- Storyboard grid export
- MP4 video reel export
- Quick Generate section for single shots
