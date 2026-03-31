# Verify Lite - Agent Guidelines

## Project Overview

Verify Lite is a simple license validation service built with FastAPI. It validates license keys against stored data and checks expiration, app matching, and active status.

## Build & Run Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_api.py

# Run a specific test
pytest tests/test_api.py::test_validate_valid_key -v

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

### Linting & Type Checking
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check with mypy
mypy main.py
```

## Code Style Guidelines

### General
- Python 3.12+ required
- Use type hints for all function parameters and return values
- Pydantic models for all request/response schemas
- Keep functions small and focused (under 50 lines preferred)

### Imports
- Standard library imports first
- Third-party imports second
- Local application imports last
- Group imports by type with blank lines between groups
- Use absolute imports over relative imports

```python
# Correct order:
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
```

### Naming Conventions
- `snake_case` for functions, variables, and module names
- `PascalCase` for classes and Pydantic models
- `SCREAMING_SNAKE_CASE` for constants
- Prefix private methods with underscore: `_private_method()`

### Type Annotations
- Always use type hints for function signatures
- Use `Optional[X]` over `X | None` for compatibility
- Use `list[X]`, `dict[X, Y]` over `List`, `Dict` (Python 3.9+)
- Pydantic models should extend `BaseModel`

```python
class ValidateRequest(BaseModel):
    key: str
    app: str

@app.post("/validate")
def validate(req: ValidateRequest) -> dict[str, bool | str]:
    ...
```

### Error Handling
- Use HTTPException for API errors with appropriate status codes
- Return `{"valid": False, "reason": "..."}` for validation failures
- Log errors appropriately using the standard `logging` module

### FastAPI Conventions
- Use `APIRouter` for grouping related endpoints
- Define request models as Pydantic `BaseModel` classes
- Use `response_model` parameter when response differs from return type
- Keep business logic in service functions, not in route handlers

### File Structure
```
verify-lite/
├── main.py              # FastAPI app and routes
├── licenses.json        # License data (not committed)
├── requirements.txt     # Dependencies
├── tests/               # Test files
│   ├── __init__.py
│   ├── test_api.py
│   └── conftest.py
└── AGENTS.md            # This file
```

### Git Conventions
- Commit message format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Keep commits atomic and focused

## Project-Specific Notes

### License Validation Logic
The validation endpoint (`POST /validate`) checks:
1. Both `key` and `app` fields are provided
2. License key exists in `licenses.json`
3. License is associated with the requested app
4. License is active (not disabled)
5. License has not expired (if expiration date is set)

### Response Format
```python
# Success
{"valid": True}

# Failure
{"valid": False, "reason": "not_found|invalid_app|disabled|expired|bad_request"}
```

### Data File
- `licenses.json` contains a `{"licenses": {...}}` structure
- Keys are license strings, values contain `app`, `active`, and optional `expires` fields
- This file is gitignored and should not be committed

## Adding New Features

1. Add Pydantic models for request/response types in `main.py`
2. Implement route handlers using FastAPI decorators
3. Add business logic in helper functions (not in routes)
4. Write tests in `tests/test_api.py`
5. Update this file if adding new conventions
