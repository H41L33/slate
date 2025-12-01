# Development Setup

This guide will get you set up to contribute to Slate. By the end, you'll have everything you need to make changes, run tests, and submit pull requests.

## Prerequisites

You'll need:

- **Python 3.14 or later**: Slate uses modern Python features
- **Git**: For version control
- **A code editor**: VS Code, PyCharm, or your favorite editor

## Step 1: Clone the Repository

```bash
git clone https://github.com/H41L33/slate.git
cd slate
```

## Step 2: Install Poetry

Poetry is Python's modern package manager. It handles dependencies, virtual environments, and packaging.

### On macOS/Linux:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### On Windows:
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Verify Installation:
```bash
poetry --version
```

## Step 3: Install Dependencies

From the project root:

```bash
poetry install
```

This creates a virtual environment and installs:
- **Runtime dependencies**: Jinja2, etc.
- **Development dependencies**: Ruff, Mypy, Pytest

## Step 4: Activate the Virtual Environment

```bash
poetry shell
```

Now `python`, `pip`, and `slate` all point to the virtual environment versions.

## Step 5: Verify Everything Works

Run the test suite:

```bash
poetry run pytest
```

You should see all tests passing (25 tests as of v0.1.6).

Run the linter:

```bash
poetry run ruff check .
```

Should report no errors.

Run the type checker:

```bash
poetry run mypy src tests
```

Should also report no errors.

## Development Tools

### Ruff (Linter)

Ruff checks your code for style issues, common mistakes, and potential bugs.

**Check for issues**:
```bash
poetry run ruff check .
```

**Auto-fix issues**:
```bash
poetry run ruff check --fix .
```

**Configuration**: See `pyproject.toml` → `[tool.ruff]`

### Mypy (Type Checker)

Mypy validates your type hints and catches type-related bugs before runtime.

**Run type check**:
```bash
poetry run mypy src tests
```

**Configuration**: See `pyproject.toml` → `[tool.mypy]`

### Pytest (Testing)

Pytest runs the test suite.

**Run all tests**:
```bash
poetry run pytest
```

**Run with verbose output**:
```bash
poetry run pytest -v
```

**Run specific test**:
```bash
poetry run pytest tests/test_parser.py::test_headings
```

**Configuration**: See `pyproject.toml` → `[tool.pytest.ini_options]`

## Making Changes

### 1. Create a Branch

Always work on a branch, never directly on `main`:

```bash
git checkout -b feature/my-awesome-feature
```

Branch naming conventions:
- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation
- `refactor/description`: Code refactoring

### 2. Make Your Changes

Edit the code in `src/slate/`. Slate uses:

- **Type hints everywhere**: `def foo(x: str) -> int:`
- **Google-style docstrings**: Clear parameter and return descriptions
- **120 character line limit**: Keeps code readable

### 3. Write Tests

Every feature needs tests! Add them to `tests/`:

```python
def test_my_feature():
    # Arrange
    input_data = "..."
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### 4. Run Quality Checks

**Before committing**, run all three checks:

```bash
# Linting
poetry run ruff check .

# Type checking
poetry run mypy src tests

# Tests
poetry run pytest
```

All three MUST pass before you push.

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add my awesome feature"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Test additions/changes
- `refactor:` Code restructuring
- `style:` Formatting changes
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/my-awesome-feature
```

Then go to GitHub and create a Pull Request from your branch to `dev`.

## IDE Configuration

### VS Code

Recommended extensions:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Ruff** (Astral)

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "python.analysis.typeCheckingMode": "strict",
  "editor.rulers": [120],
  "files.trimTrailingWhitespace": true
}
```

### PyCharm

1. Enable mypy:
   - Preferences → Tools → Python Integrated Tools
   - Select "Mypy" for type checker

2. Configure Ruff:
   - Preferences → Tools → External Tools
   - Add Ruff as external tool

3. Set test runner:
   - Preferences → Tools → Python Integrated Tools
   - Set "pytest" as default test runner

## Common Tasks

### Running Slate Locally

```bash
poetry run slate build test.md test.html -T templates/basic.html
```

### Installing Slate for System-Wide Use

```bash
poetry build
pipx install dist/slate_md-0.1.6-py3-none-any.whl
```

### Updating Dependencies

```bash
poetry update
```

### Adding a New Dependency

```bash
poetry add package-name
```

### Removing a Dependency

```bash
poetry remove package-name
```

## Troubleshooting

### "Command not found: poetry"

Poetry isn't in your PATH. Add this to your shell config (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### "No module named 'slate'"

You're not in the Poetry virtual environment. Run:

```bash
poetry shell
```

### Tests Are Failing

1. Make sure you're on the latest `dev` branch
2. Run `poetry install` to update dependencies
3. Check if there are uncommitted changes affecting tests

### Mypy Errors About Missing Type Stubs

Some packages don't have type stubs. That's okay! You can:

1. Add to `pyproject.toml` → `[tool.mypy]`:
   ```toml
   ignore_missing_imports = true
   ```
2. Or install stub packages: `poetry add --group dev types-package-name`

## Next Steps

- Read the [Codebase Guide](codebase_guide.md) to understand the architecture
- Check the [CI Workflow](ci_workflow.md) to learn our quality standards
- Look at existing tests for examples

## Getting Help

- **Questions about code**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Feature ideas**: Open a GitHub Issue with the "enhancement" label

Happy hacking! 🚀
