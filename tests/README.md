# Tests for FIBO Continuity Director

This directory contains unit tests for the application.

## Running Tests

```bash
cd fibo_continuity_director
pytest tests/ -v
```

## Test Structure

- `test_planner.py` - Tests for shot planning logic
- `test_validator.py` - Tests for color/continuity validation
- `test_helpers.py` - Tests for utility functions (grid, video, save/load)
- `test_client.py` - Tests for API client (with mocks)

## Adding Tests

1. Add pytest to requirements: `pip install pytest`
2. Create test files matching pattern `test_*.py`
3. Use fixtures for common setup
