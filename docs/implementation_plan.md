# FIBO Continuity Director - Improvement Report

> Comprehensive audit and roadmap for making this project production-ready.

---

## 🚨 Critical Issues (Fix Immediately)

### 1. Corrupted `requirements.txt`
**File:** [requirements.txt](file:///c:/Users/snigd/OneDrive/Documents/Projects/fibo_continuity_director/requirements.txt)

The file contains null bytes/unicode corruption on line 8-9:
```
p\0y\0t\0h\0o\0n\0-\0d\0o\0t\0e\0n\0v\0
```

**Fix:** Replace with clean version:
```txt
streamlit
requests
pydantic
pillow
numpy
moviepy
python-dotenv
```

---

### 2. `scripts/verify.py` Uses Wrong Import
**File:** [verify.py](file:///c:/Users/snigd/OneDrive/Documents/Projects/fibo_continuity_director/scripts/verify.py#L10)

```python
from app.models.config import BRIA_BASE_URL, FIBO_API_KEY  # WRONG
```
Should be:
```python
from app.models.config import FIBO_API_URL, FIBO_API_KEY
```

---

### 3. API Key Exposure in `.env`
**File:** [.env](file:///c:/Users/snigd/OneDrive/Documents/Projects/fibo_continuity_director/.env)

The `.env` file contains a real API key. Add `.env` to `.gitignore` before pushing to GitHub!

---

## ⚡ Performance Issues

| Issue | Location | Solution |
|-------|----------|----------|
| **Slow polling** | `client.py` L89-108 | 1s delay between polls. Consider exponential backoff. |
| **No parallel generation** | `engine.py` | Shots generated sequentially. Could batch first shot's completion trigger for shots 2+ |
| **Full re-render on small changes** | `main.py` | Changing one setting regenerates entire sequence. Add partial update support. |

---

## 🎨 UX Improvements Needed

### High Priority
1. **Loading states unclear** - Add spinner text showing "Generating Shot 3/5: Medium character-focused shot"
2. **Error messages too technical** - "422 Unprocessable Entity" should say "Invalid prompt format"
3. **No cancel button** - Users can't stop mid-generation
4. **Session loss on refresh** - All generated images lost on page refresh

### Medium Priority
5. **No image zoom** - Add lightbox/modal for full-size image preview
6. **No undo/redo** - Can't revert to previous versions of shots
7. **Export naming** - Files saved as UUID (`0beb6dee_storyboard.png`) - use project name
8. **No dark mode toggle** - Hardcoded dark theme

---

## 🛠️ Code Quality Issues

### Missing Type Hints
```python
# Current (engine.py)
def build_fibo_payload(continuity_map, shot):

# Should be
def build_fibo_payload(continuity_map: ContinuityMap, shot: ShotSpec) -> Dict[str, Any]:
```

### Inconsistent Error Handling
- `client.py` logs errors but returns placeholder images silently
- User never sees why their image failed

### No Unit Tests
Create `tests/` directory with:
- `test_planner.py` - Verify shot generation logic
- `test_validator.py` - Verify color distance calculations  
- `test_client.py` - Mock API responses

---

## 🚀 Feature Roadmap

### Phase 1: Core Stability (This Week)
- [ ] Fix corrupted requirements.txt
- [ ] Fix verify.py import
- [ ] Add `.gitignore` with `.env`, `outputs/`, `debug.log`
- [ ] Add error toasts instead of silent failures
- [ ] Save/load projects to JSON files

### Phase 2: UX Polish (Next Week)
- [ ] Project history sidebar (list past projects)
- [ ] Image zoom modal
- [ ] Cancel generation button
- [ ] Better progress indicators with ETA
- [ ] Keyboard shortcuts (Ctrl+G = generate, Esc = cancel)

### Phase 3: Advanced Features (Future)
- [ ] Real LLM integration (replace mock planner with GPT-4/Gemini)
- [ ] CLIP-based character consistency validation
- [ ] Batch export (ZIP with all shots + JSON plan)
- [ ] Team collaboration (share project links)
- [ ] A/B testing mode (generate 2 variants per shot)

---

## 📁 Missing Files

| File | Purpose |
|------|---------|
| `.gitignore` | Exclude `.env`, `outputs/`, `__pycache__/`, `debug.log` |
| `tests/` directory | Unit tests |
| `CHANGELOG.md` | Version history |
| `LICENSE` | Open source license if applicable |

---

## Summary Priorities

| Priority | Task | Effort |
|----------|------|--------|
| 🔴 P0 | Fix requirements.txt corruption | 5 min |
| 🔴 P0 | Fix verify.py import | 5 min |
| 🔴 P0 | Add .gitignore | 5 min |
| 🟡 P1 | Session persistence (localStorage) | 2 hrs |
| 🟡 P1 | Better error messages | 1 hr |
| 🟢 P2 | Image zoom modal | 1 hr |
| 🟢 P2 | Project history | 3 hrs |
