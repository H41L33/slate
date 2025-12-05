# Contributing to Slate

## Development Setup

Slate uses [Poetry](https://python-poetry.org/) for dependency management.

1.  **Install Poetry**: Follow the instructions on the Poetry website.
2.  **Install Dependencies**:
    ```bash
    poetry install
    ```
3.  **Run Tests**:
    ```bash
    poetry run pytest
    ```

## Code Style

We use `ruff` for linting and formatting.

```bash
poetry run ruff check .
poetry run ruff format .
```

## Project Structure

-   `src/slate`: Source code.
-   `tests`: Test suite.
-   `documentation`: Documentation for humans and machines.
