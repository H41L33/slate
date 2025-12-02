"""
Tests for verifying that the Slate CLI tool correctly generates output
in multiple formats (HTML, Gemini, Gopher) from a single Markdown input.
It also includes tests for dynamic date and time placeholder replacement.
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
        # Re-raise it as an exception to mark the test as failed if exit code is not 0.
        if e.code != 0:
            raise ValueError(f"CLI exited with error code {e.code}") from e
    finally:
        # Always restore the original sys.argv, even if an error occurred.
        sys.argv = old_argv


def test_multi_format_outputs(tmp_path: Path):
    """Tests the generation of HTML, Gemini, and Gopher outputs from a single Markdown source.

    This test verifies that various Markdown elements (headings, paragraphs,
    lists, blockquotes, code blocks, images) are correctly rendered into
    each of the supported output formats.
    """
    # Define paths for input Markdown, HTML template, and output files.
    md_input_path = tmp_path / "sample.md"
    html_template_path = tmp_path / "template.html"
    output_html_path = tmp_path / "out" / "page.html"
    output_gemini_path = tmp_path / "out" / "page.gmi"
    output_gopher_path = tmp_path / "out" / "page.gph"

    # Markdown content with various block types for testing.
    markdown_content = """
# Sample Title

A paragraph with `inline` code.

- item one
- item two

> A quote

```python
print("hi")
```

![Alt text](http://example.com/img.png "Caption here")
"""
    # Write the Markdown content to the input file.
    write_file(md_input_path, markdown_content)
    
    # Minimal Jinja2 template for HTML output.
    html_template_content = "<html><head><title>{{ title }}</title></head><body>{{ content }}</body></html>"
    # Write the HTML template to its file.
    write_file(html_template_path, html_template_content)

    # --- Test HTML Output ---
    # Run the CLI tool to generate HTML output.
    run_main_with_args(["page", str(md_input_path), str(output_html_path), "-T", str(html_template_path), "-f", "html"])
    # Assert that the HTML output file was created.
    assert output_html_path.exists()
    # Read and verify content in the generated HTML.
    generated_html = output_html_path.read_text(encoding="utf-8")
    assert "Sample Title" in generated_html
    assert "A paragraph with" in generated_html
    assert "<code" in generated_html or "<code>" in generated_html # Check for inline code rendering.
    assert 'content-ul' in generated_html # Check for list rendering.
    assert "content-blockquote" in generated_html # Check for blockquote rendering.

    # --- Test Gemini Output ---
    # Run the CLI tool to generate Gemini (Gemtext) output.
    run_main_with_args(["page", str(md_input_path), str(output_gemini_path), "-f", "gemini"])
    # Assert that the Gemini output file was created.
    assert output_gemini_path.exists()
    # Read and verify content in the generated Gemtext.
    generated_gemini = output_gemini_path.read_text(encoding="utf-8")
    assert "# Sample Title" in generated_gemini
    assert "A paragraph with" in generated_gemini
    assert "* item one" in generated_gemini or "item one" in generated_gemini # Check for list item rendering.
    assert "A quote" in generated_gemini
    assert "print(\"hi\")" in generated_gemini # Check for code block rendering.

    # --- Test Gopher Output ---
    # Run the CLI tool to generate Gophermap output.
    run_main_with_args(["page", str(md_input_path), str(output_gopher_path), "-f", "gopher"])
    # Assert that the Gopher output file was created.
    assert output_gopher_path.exists()
    # Read and verify content in the generated Gophermap.
    generated_gopher = output_gopher_path.read_text(encoding="utf-8")
    assert "Sample Title" in generated_gopher
    assert "A paragraph with" in generated_gopher
    assert "item one" in generated_gopher # Check for list item rendering.
    assert "print(\"hi\")" in generated_gopher # Check for code block rendering.


def test_date_time_placeholders(tmp_path: Path):
    """Tests the correct replacement of `{{date}}` and `{{time}}` placeholders across formats.

    This test ensures that the CLI tool correctly substitutes dynamic date and
    time values into Markdown content for HTML, Gemini, and Gopher outputs.
    """
    import datetime  # Import datetime for generating current date/time strings.
    
    # Define paths for input Markdown, HTML template, and output files.
    markdown_input_path = tmp_path / "dt.md"
    html_template_path = tmp_path / "dt_template.html"
    output_html_path = tmp_path / "out" / "dt.html"
    output_gemini_path = tmp_path / "out" / "dt.gmi"
    output_gopher_path = tmp_path / "out" / "dt.gph"

    # Markdown content containing date and time placeholders.
    markdown_content_with_placeholders = """
# Title with {{creation_date}}

Paragraph with {{creation_time}}.
"""
    write_file(markdown_input_path, markdown_content_with_placeholders)
    
    # HTML template that also uses date and time placeholders.
    html_template_with_placeholders = "<html><head><title>{{ title }}</title></head><body>{{ content }}<p>{{ creation_date }} - {{ creation_time }}</p></body></html>"
    write_file(html_template_path, html_template_with_placeholders)

    # Get current date and time formatted as expected by the renderers.
    now = datetime.datetime.now()
    formatted_date_string = now.strftime("%d/%m/%Y")
    formatted_time_string = now.strftime("%H:%M")

    # --- Test HTML Output with Placeholders ---
    # --- Test HTML Output with Placeholders ---
    run_main_with_args(["page", str(markdown_input_path), str(output_html_path), "-T", str(html_template_path), "-f", "html"])
    assert output_html_path.exists()
    generated_html_content = output_html_path.read_text(encoding="utf-8")
    # Verify that both date and time strings are present in the HTML output.
    assert formatted_date_string in generated_html_content
    assert formatted_time_string in generated_html_content

    # --- Test Gemini Output with Placeholders ---
    # --- Test Gemini Output with Placeholders ---
    run_main_with_args(["page", str(markdown_input_path), str(output_gemini_path), "-f", "gemini"])
    assert output_gemini_path.exists()
    generated_gemini_content = output_gemini_path.read_text(encoding="utf-8")
    # Verify that date and time strings are correctly rendered in Gemtext headings and paragraphs.
    assert f"# Title with {formatted_date_string}" in generated_gemini_content
    assert f"Paragraph with {formatted_time_string}." in generated_gemini_content

    # --- Test Gopher Output with Placeholders ---
    # --- Test Gopher Output with Placeholders ---
    run_main_with_args(["page", str(markdown_input_path), str(output_gopher_path), "-f", "gopher"])
    assert output_gopher_path.exists()
    generated_gopher_content = output_gopher_path.read_text(encoding="utf-8")
    # Verify that date and time strings are correctly rendered in Gophermap informational lines.
    assert f"iTitle with {formatted_date_string}" in generated_gopher_content
    assert f"iParagraph with {formatted_time_string}." in generated_gopher_content