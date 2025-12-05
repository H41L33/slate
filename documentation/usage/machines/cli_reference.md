# Slate CLI Reference

## Global Options

-   `-v`, `--version`: Show version and exit.
-   `-h`, `--help`: Show help message and exit.

## Commands

### `slate draft`

Create a new Slate project with a basic directory structure.

**Usage:**
```bash
slate draft <name>
```

**Arguments:**
-   `name`: Name of the new site (directory to be created).

---

### `slate build`

Build the static site or a single page.

**Usage:**
```bash
slate build [target] [options]
```

**Arguments:**
-   `target`: (Optional) The directory (site) or file (page) to build. Defaults to current directory (`.`).

**Options:**
-   `-o OUTPUT`, `--output OUTPUT`: Output directory (for site) or file (for page).
-   `-T TEMPLATES`, `--templates TEMPLATES`: Templates directory (default: `templates/`).
-   `--template TEMPLATE`: Path to a specific Jinja2 template (required for single page HTML builds).
-   `--structure {flat,tree}`: Output structure (default: `tree`).
-   `--clean`: Safely clean output directory before building.
-   `--dry-run`: Simulate actions without making changes.
-   `--formats FORMATS`: Comma-separated list of output formats (e.g. `html,gemini,gopher`).
-   `--ipfs`: Enable IPFS compatibility (forces relative links).
-   `-f FORMAT`, `--format FORMAT`: Output format (single). Legacy option.

**Page-Specific Options:**
-   `-t TITLE`, `--title TITLE`: Title override.
-   `-d DESCRIPTION`, `--description DESCRIPTION`: Brief description.

---

### `slate rebuild`

Re-run the last executed command. Useful for rapid iteration.

**Usage:**
```bash
slate rebuild
```
