---
description: Run CI checks locally (Ruff, MyPy, Pytest)
---

This workflow runs the same checks as the CI pipeline to ensure code quality before committing.

1. Run Linting (Ruff)
// turbo
```bash
poetry run ruff check .
```

2. Run Type Checking (MyPy)
// turbo
```bash
poetry run mypy src tests
```

3. Run Tests (Pytest)
// turbo
```bash
poetry run pytest
```
