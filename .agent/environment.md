# Slate: Development Environment

## Python Version
**Required**: Python 3.14+  
**Why 3.14**: Latest features, modern type hints, performance improvements

## Package Manager: Poetry
**Version**: Latest stable  
**Purpose**: Dependency management, virtual environments, packaging

### Poetry Commands
```bash
poetry install          # Install all dependencies
poetry add <package>    # Add new dependency
poetry run <command>    # Run command in venv
poetry build            # Build distribution packages
poetry publish          # Publish to PyPI
```

## Development Dependencies

### Ruff (Linter)
**Purpose**: Fast Python linter (replaces flake8, isort, etc.)  
**Command**: `poetry run ruff check .`  
**Config**: `pyproject.toml` → `[tool.ruff]`  
**Rules**: Line length 120, select E/F/W rules

### Mypy (Type Checker)
**Purpose**: Static type checking  
**Command**: `poetry run mypy src tests`  
**Config**: `pyproject.toml` → `[tool.mypy]`  
**Strictness**: Strict mode enabled

### Pytest (Test Runner)
**Purpose**: Unit and integration testing  
**Command**: `poetry run pytest`  
**Config**: `pyproject.toml` → `[tool.pytest.ini_options]`  
**Coverage**: Aim for 100%

## Runtime Dependencies

### Core
- `jinja2`: Template rendering
- `markdown`: (Not used directly, custom parser)
- `pathlib`: File operations (stdlib)
- `argparse`: CLI (stdlib)
- `importlib.metadata`: Version info (stdlib)

### No Heavy Dependencies
Intentionally minimal to keep package lightweight and fast.

## Project Structure Requirements

### Source Code
**Location**: `src/slate/`  
**Format**: PEP 420 namespace package  
**Imports**: `from slate.main import ...`

### Tests
**Location**: `tests/`  
**Naming**: `test_*.py`  
**Structure**: Mirror source structure

## Development Workflow

### 1. Setup
```bash
git clone <repo>
cd slate
poetry install
```

### 2. Development Cycle
```bash
# Make changes to src/slate/*.py
poetry run ruff check .        # Lint
poetry run mypy src tests      # Type check
poetry run pytest              # Test
```

### 3. Pre-Commit (MANDATORY)
```bash
# Run ALL CI checks locally
poetry run ruff check .
poetry run mypy src tests
poetry run pytest -q
```

### 4. Commit
```bash
git add .
git commit -m "feat: description"
git push origin <branch>
```

## IDE Configuration

### VS Code
Recommended extensions:
- Python (Microsoft)
- Pylance (Microsoft)
- Ruff (Astral)

Settings:
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "python.analysis.typeCheckingMode": "strict"
}
```

### PyCharm
- Enable mypy plugin
- Configure Ruff as external tool
- Set pytest as default test runner

## Environment Variables
**None required**. Slate uses no environment configuration.

## Virtual Environment
Poetry creates venv automatically in:
- macOS/Linux: `~/.cache/pypoetry/virtualenvs/`
- Windows: `%LOCALAPPDATA%\pypoetry\virtualenvs\`

Activate manually:
```bash
poetry shell
```

## Python Path
Package installed in editable mode: `pip install -e .`  
Changes to source reflected immediately without reinstall.

## Type Hints Standard
- All functions: Type hints for args + return
- Variables: Annotate where type unclear
- Use `from typing import Any` for dicts
- Prefer `str | None` over `Optional[str]`

## Testing Requirements
- Every feature: Corresponding test
- CLI commands: Integration tests
- Parsers/renderers: Unit tests
- Mock file I/O: Use `tempfile.mkdtemp()`
- Assert coverage: Aim for 100%

## Code Style
- Line length: 120 characters
- Indentation: 4 spaces (no tabs)
- Quotes: Double quotes preferred
- Imports: Stdlib → 3rd party → local
- Docstrings: Google style

## Performance Considerations
- No premature optimization
- Profile before optimizing
- Prefer clarity over micro-optimizations
- Regex compiled once (module level)

## Security
- No user input executed
- All file paths validated
- HTML escaped by default
- No shell commands
- No eval/exec

## Distribution
**Platform**: PyPI as `slate-md`  
**Entry point**: `slate` command  
**Install method**: `pipx install slate-md` (recommended)
