# CI Workflow Guide

Continuous Integration (CI) is how we ensure Slate stays reliable and high-quality. This guide explains our CI system and what you need to know to work with it.

## The Golden Rule

**⚠️ You MUST run all CI checks locally before pushing to `main` or creating a pull request.**

This isn't optional. It's how we keep the codebase clean and prevent broken code from landing in production.

## What is CI?

CI (Continuous Integration) automatically runs tests and checks whenever you push code to GitHub. If something's wrong, the CI build fails and you'll know immediately.

Our CI checks three things:
1. **Linting** (Ruff): Is the code style correct?
2. **Type Checking** (Mypy): Are the types correct?
3. **Testing** (Pytest): Does everything work?

## Running CI Locally

Before pushing code, run these three commands:

```bash
# 1. Lint
poetry run ruff check .

# 2. Type check
poetry run mypy src tests

# 3. Test
poetry run pytest
```

All three MUST pass with zero errors.

### Using the Pre-Commit Workflow

We have a shortcut workflow (`:pre_commit`) that runs all three checks:

```bash
# Just run this:
poetry run ruff check .
poetry run mypy src tests
poetry run pytest -q
```

If you see any failures, fix them before pushing.

## Understanding CI Failures

### Ruff Failures (Linting)

**What it means**: Your code has style issues

**Example error**:
```
main.py:42:80: E501 Line too long (125 > 120 characters)
```

**How to fix**:
1. Review the error message
2. Run `poetry run ruff check --fix .` to auto-fix simple issues
3. Manually fix remaining issues
4. Re-run `poetry run ruff check .` to verify

### Mypy Failures (Type Checking)

**What it means**: Your type hints are wrong or missing

**Example error**:
```
main.py:42: error: Argument 1 to "render_html" has incompatible type "str"; expected "list[dict[str, Any]]"
```

**How to fix**:
1. Add missing type hints
2. Fix type mismatches
3. Use proper types (`str | None` instead of `Optional[str]`)
4. Re-run `poetry run mypy src tests` to verify

### Pytest Failures (Testing)

**What it means**: Your changes broke something

**Example error**:
```
FAILED tests/test_parser.py::test_headings - AssertionError: assert [] == [{'h1': 'Hello'}]
```

**How to fix**:
1. Run the specific test: `poetry run pytest tests/test_parser.py::test_headings -v`
2. Debug the failure
3. Fix the code or update the test
4. Re-run all tests: `poetry run pytest`

## The CI Pipeline

When you push code, GitHub Actions runs this workflow:

### Step 1: Setup
- Checks out your code
- Installs Python 3.14
- Installs Poetry
- Installs dependencies with `poetry install`

### Step 2: Lint
- Runs `poetry run ruff check .`
- **Blocks merge if it fails**

### Step 3: Type Check
- Runs `poetry run mypy src tests`
- **Blocks merge if it fails**

### Step 4: Test
- Runs `poetry run pytest -q`
- **Blocks merge if it fails**

The entire pipeline takes about 1-2 minutes.

## Branch Protection

### `main` Branch

The `main` branch is **protected**:
- ✅ All CI checks must pass
- ✅ Pull requests required
- ❌ No direct pushes allowed
- ❌ No force pushes allowed

### `dev` Branch

The `dev` branch has lighter protection:
- ✅ All CI checks must pass
- ❌ Can force push (with `--force-with-lease`)

## Pull Request Workflow

### Creating a PR

1. Push your branch to GitHub
2. Go to the repository on GitHub
3. Click "Compare & pull request"
4. Fill in the PR description:
   - What does this change?
   - Why is it needed?
   - How was it tested?
5. Submit the PR

### Watching CI Run

After submitting, you'll see CI checks running:

![CI Status]
- ⏳ Yellow dot: In progress
- ✅ Green check: Passed
- ❌ Red X: Failed

Click "Details" on any check to see the full output.

### If CI Fails

1. Read the error message
2. Fix the issue locally
3. Run CI checks locally to verify
4. Push the fix
5. CI will automatically re-run

Don't merge until CI is green!

## Hotfix Workflow

Sometimes you need to fix a critical bug in production quickly.

### Process

1. Create a hotfix branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix-v0.1.X
   ```

2. Make your fix

3. **Run CI locally** (still mandatory!):
   ```bash
   poetry run ruff check .
   poetry run mypy src tests
   poetry run pytest
   ```

4. Push and create PR to `main`

5. After merging, sync `dev`:
   ```bash
   git checkout dev
   git merge main
   git push origin dev
   ```

## Release Workflow

### From Dev to Main

When `dev` is ready for release:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.7"
   ```

2. Update `CHANGELOG.md` with release notes

3. Ensure all CI checks pass on `dev`

4. Create PR from `dev` to `main`

5. After merge, tag the release:
   ```bash
   git checkout main
   git pull origin main
   git tag v0.1.7
   git push origin v0.1.7
   ```

## Debugging CI Failures

### Viewing Full Logs

1. Go to GitHub Actions tab
2. Click the failed workflow
3. Click the failed step
4. Read the full output

### Reproducing Locally

Match the CI environment:

```bash
# Check Python version
python --version  # Should be 3.14.x

# Clean install
rm -rf .venv
poetry install --no-interaction

# Run checks
poetry run ruff check .
poetry run mypy src tests
poetry run pytest -q
```

### Common Issues

**"Tests pass locally but fail in CI"**
- Check for hardcoded paths (use `Path.home()` etc.)
- Check for timezone issues (use UTC in tests)
- Check for file permissions

**"CI is stuck on pending"**
- GitHub Actions might be down
- Check GitHub's status page
- Re-run the workflow after a few minutes

**"Dependencies failing to install"**
- Check `pyproject.toml` for syntax errors
- Ensure all dependencies are available on PyPI
- Check Poetry lock file is committed

## Best Practices

### 1. Run CI Before Pushing

Always run the full CI suite locally:
```bash
poetry run ruff check .
poetry run mypy src tests
poetry run pytest
```

### 2. Fix Failures Immediately

Don't let broken CI sit. Fix it ASAP or revert your changes.

### 3. Keep PRs Small

Smaller PRs = easier reviews = faster merges

### 4. Write Good Commit Messages

```bash
# Good
git commit -m "fix: handle empty Markdown files gracefully"

# Bad
git commit -m "fix stuff"
```

### 5. Test Edge Cases

Don't just test the happy path. Test:
- Empty inputs
- Invalid inputs
- Boundary conditions
- Error cases

## CI Configuration

The CI workflow is defined in `.github/workflows/ci.yml`.

**Don't modify this file unless you know what you're doing!**

If you need to change CI behavior:
1. Discuss in a GitHub Issue first
2. Test changes with `act` (local GitHub Actions runner)
3. Document changes in the PR

## Performance Targets

Our CI should be fast:
- **Total time**: < 2 minutes
- **Ruff**: < 5 seconds
- **Mypy**: < 10 seconds
- **Pytest**: < 30 seconds

If CI gets slower, we need to investigate why.

## Quality Gates

To merge code, you must have:
- ✅ Zero Ruff violations
- ✅ Zero Mypy errors
- ✅ 100% test pass rate
- ✅ No regressions in existing tests

There are **no exceptions** to these rules.

## Summary

CI exists to protect code quality. By running checks locally before pushing, you:
- Catch bugs early
- Save time (no waiting for CI to fail)
- Keep the codebase clean
- Make reviewers happy

**Remember**: Local CI checks are mandatory, not optional!

---

Questions about CI? Open a GitHub Discussion or check the [Development Setup](development_setup.md) guide.
