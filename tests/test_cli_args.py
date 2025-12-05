"""
Tests for verifying the correct parsing and handling of command-line
arguments by the Slate CLI tool. This includes ensuring that various
output formats (HTML, Gemini, Gopher) are generated correctly based on
the provided input and options.
"""

import sys
from pathlib import Path

from slate import main as slate_main  # Import slate.main globally once


def write_file(path: Path, content: str):
    """Writes the given content to a file, creating parent directories if necessary.

    Args:
        path: The pathlib.Path object representing the file to write to.
        content: The string content to write into the file.
    """
    # Create any necessary parent directories for the file.
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write the content to the file with UTF-8 encoding.
    path.write_text(content, encoding="utf-8")


def run_main_with_args(args: list[str]):
    """Helper function to run the Slate CLI's main function with a given set of arguments.

    This function temporarily modifies `sys.argv` to simulate command-line
    execution, ensuring that the CLI's argument parsing and execution flow
    can be tested in isolation. It restores `sys.argv` after execution.

    Args:
        args: A list of strings representing the command-line arguments
              to pass to the Slate CLI (e.g., `["-i", "input.md"]`).
    """
    # Store the original sys.argv to restore it after the test.
    old_argv = sys.argv[:]
    # Replace sys.argv with the simulated command-line arguments.
    sys.argv = ["slate"] + args
    try:
        # Execute the main function of the Slate CLI.
        slate_main.main()
    except SystemExit as e:
        # argparse raises SystemExit on errors, which pytest catches.
        # Re-raise it as an exception to mark the test as failed.
        if e.code != 0:
            raise ValueError(f"CLI exited with error code {e.code}") from e
    finally:
        # Always restore the original sys.argv, even if an error occurred.
        sys.argv = old_argv


def test_html_output(tmp_path):
    """Tests that HTML output is correctly generated with basic Markdown input.

    Verifies that the CLI tool can process a Markdown file, apply a Jinja2
    template, and produce an HTML file containing the expected title and
    paragraph content.
    """
    md_file_path = tmp_path / "input.md"
    template_file_path = tmp_path / "template.html"
    output_html_path = tmp_path / "out" / "page.html"

    # Prepare Markdown input and a minimal HTML template.
    markdown_content = "# Title\\n\\nThis is a paragraph."
    write_file(md_file_path, markdown_content)

    html_template_content = (
        "<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>"
    )
    write_file(template_file_path, html_template_content)

    # Run the CLI tool to generate HTML output.
    # Unified CLI: slate build input.md -o output.html -T template.html -f html
    run_main_with_args(
        [
            "build",
            str(md_file_path),
            "-o",
            str(output_html_path),
            "--template",
            str(template_file_path),
            "-f",
            "html",
        ]
    )

    # Assertions to check the generated HTML file.
    assert output_html_path.exists(), (
        f"Expected output file created at {output_html_path}"
    )
    generated_html_content = output_html_path.read_text(encoding="utf-8")
    assert "Title" in generated_html_content
    assert "This is a paragraph." in generated_html_content


def test_gemini_output(tmp_path):
    """Tests that Gemtext output is correctly generated with basic Markdown input.

    Verifies that the CLI tool can process a Markdown file and produce a
    Gemtext file containing the expected heading and paragraph content.
    """
    md_file_path = tmp_path / "gmi.md"
    output_gemini_path = tmp_path / "page.gmi"
    markdown_content = "# Gemini\\n\\nA gemini paragraph."
    write_file(md_file_path, markdown_content)

    # Run the CLI tool to generate Gemtext output.
    run_main_with_args(
        ["build", str(md_file_path), "-o", str(output_gemini_path), "-f", "gemini"]
    )

    # Assertions to check the generated Gemtext file.
    assert output_gemini_path.exists()
    generated_gemini_content = output_gemini_path.read_text(encoding="utf-8")
    assert "# Gemini" in generated_gemini_content
    assert "A gemini paragraph." in generated_gemini_content


def test_gopher_output(tmp_path):
    """Tests that Gophermap output is correctly generated with basic Markdown input.

    Verifies that the CLI tool can process a Markdown file and produce a
    Gophermap-like text file containing the expected content.
    """
    md_file_path = tmp_path / "gopher.md"
    output_gopher_path = tmp_path / "page.gph"
    markdown_content = "# Gopher\\n\\nA gopher paragraph."
    write_file(md_file_path, markdown_content)

    # Run the CLI tool to generate Gophermap output.
    run_main_with_args(
        ["build", str(md_file_path), "-o", str(output_gopher_path), "-f", "gopher"]
    )

    # Assertions to check the generated Gophermap file.
    assert output_gopher_path.exists()
    generated_gopher_content = output_gopher_path.read_text(encoding="utf-8")
    assert "Gopher" in generated_gopher_content
    assert "A gopher paragraph." in generated_gopher_content


def test_draft_command(tmp_path):
    """Tests that the draft command creates a new site structure."""
    site_name = "my-site"
    site_path = tmp_path / site_name

    run_main_with_args(["draft", str(site_path)])

    assert site_path.exists()
    assert (site_path / "content" / "index.md").exists()
    assert (site_path / "templates" / "base.html").exists()
    assert (site_path / "static" / "style.css").exists()


def test_rebuild_command(tmp_path):
    """Tests that the rebuild command re-runs the last command."""
    # First run a command to populate slate.json
    md_file_path = tmp_path / "rebuild.md"
    output_path = tmp_path / "rebuild.html"
    template_path = tmp_path / "template.html"

    write_file(md_file_path, "# Rebuild")
    write_file(template_path, "{{ content }}")

    run_main_with_args(
        [
            "build",
            str(md_file_path),
            "-o",
            str(output_path),
            "--template",
            str(template_path),
        ]
    )

    assert output_path.exists()
    output_path.unlink()  # Delete output to verify rebuild works
    assert not output_path.exists()

    # Run rebuild
    run_main_with_args(["rebuild"])

    assert output_path.exists()
