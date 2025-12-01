# Slate: CI Requirements

## CRITICAL RULE
⚠️ **MANDATORY**: Run ALL CI checks locally BEFORE merging to `main` or creating PR.

## CI Workflow Location
`.github/workflows/ci.yml`

## CI Checks (Must Pass)

### 1. Ruff (Linting)
```bash
poetry run ruff check .
```
**Purpose**: Code style, syntax errors, common mistakes  
**Must**: Zero errors, zero warnings  
**Fixes**: `poetry run ruff check --fix .`

### 2. Mypy (Type Checking)
```bash
poetry run mypy src tests
```
**Purpose**: Static type validation  
**Must**: Zero type errors  
**Target**: `src/` and `tests/` directories

### 3. Pytest (Testing)
```bash
poetry run pytest -q
```
**Purpose**: Functional correctness  
**Must**: All tests pass (25/25 as of v0.1.6)  
**Coverage**: Aim for 100%

## Local Pre-Commit Workflow

### Automated Script (Recommended)
Use the `/pre_commit` workflow:
```bash
# Runs all three checks in sequence
poetry run ruff check .
poetry run mypy src tests
poetry run pytest -q
```

### Manual Execution
```bash
# 1. Lint
poetry run ruff check .
# Fix issues if any
poetry run ruff check --fix .

# 2. Type check
poetry run mypy src tests
# Fix type errors manually

# 3. Test
poetry run pytest
# Fix failing tests
```

## CI Pipeline Stages

### Stage 1: Checkout
- Clones repository
- Checks out PR branch

### Stage 2: Setup Python
- Installs Python 3.14
- Caches pip packages

### Stage 3: Install Poetry
- Upgrades pip
- Installs Poetry

### Stage 4: Install Dependencies
- Runs `poetry install --no-interaction`
- Installs runtime + dev dependencies

### Stage 5: Ruff Lint
- Executes `poetry run ruff check .`
- **Blocks merge** if errors found

### Stage 6: Mypy Type Check
- Executes `poetry run mypy src tests`
- **Blocks merge** if type errors found

### Stage 7: Pytest
- Executes `poetry run pytest -q`
- **Blocks merge** if tests fail

## CI Triggers

### Push Events
- Branch: `main`
- Branch: `dev`

### Pull Request Events
- Target: `main`
- Target: `dev`

## Failure Handling

### If Ruff Fails
1. Review error output
2. Run `poetry run ruff check --fix .` for auto-fixes
3. Manually fix remaining issues
4. Re-run `poetry run ruff check .`
5. Commit fixes

### If Mypy Fails
1. Review type error messages
2. Add missing type hints
3. Fix type mismatches
4. Re-run `poetry run mypy src tests`
5. Commit fixes

### If Pytest Fails
1. Review test output
2. Identify failing test
3. Debug with `poetry run pytest -v`
4. Fix code or test
5. Re-run `poetry run pytest`
6. Commit fixes

## Branch Protection

### `main` Branch
- **Protected**: Yes
- **Require CI pass**: Yes
- **Require reviews**: Recommended
- **No force push**: Enforced

### `dev` Branch
- **Protected**: Yes (lighter)
- **Require CI pass**: Yes
- **Allow force push**: With lease

## Merge Strategy

### Feature → Dev
1. Create feature branch from `dev`
2. Implement feature
3. **Run CI locally** (MANDATORY)
4. Push to remote
5. Create PR to `dev`
6. Wait for CI ✅
7. Merge (squash or merge commit)

### Dev → Main (Release)
1. Ensure `dev` CI passing
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Create PR from `dev` to `main`
5. Wait for CI ✅
6. Merge (merge commit preferred)
7. Tag release: `git tag v0.1.X`
8. Push tag: `git push origin v0.1.X`

## Hotfix Workflow

### Critical Bugs in Main
1. Create `hotfix-vX.X.X` from `main`
2. Fix bug
3. **Run CI locally** (MANDATORY)
4. PR to `main`
5. Merge after CI ✅
6. Cherry-pick to `dev` or merge `main` → `dev`

## Performance Targets
- Total CI time: < 2 minutes
- Ruff: < 5 seconds
- Mypy: < 10 seconds
- Pytest: < 30 seconds

## Debugging CI Failures

### View Logs
1. Go to GitHub Actions tab
2. Click failed workflow
3. Click failed step
4. Expand log output

### Reproduce Locally
```bash
# Match CI environment
python --version  # Should be 3.14
poetry install --no-interaction
poetry run ruff check .
poetry run mypy src tests
poetry run pytest -q
```

## CI Configuration Changes

### Modifying `.github/workflows/ci.yml`
1. Test changes locally with `act` (GitHub Actions local runner)
2. Create PR with CI changes
3. Monitor first run carefully
4. Document changes in PR description

## Quality Gates
- **Ruff**: Zero violations
- **Mypy**: Zero type errors
- **Pytest**: 100% pass rate
- **Coverage**: 80%+ (aspirational: 100%)

## Exceptions
**None**. CI must pass for all merges to `main` and `dev`. No bypassing.

## Tools Not in CI (But Recommended)
- `coverage`: Track test coverage
- `bandit`: Security linting
- `black`: Code formatting (Ruff handles this)
- `isort`: Import sorting (Ruff handles this)

All functionality consolidated in Ruff + Mypy + Pytest.
