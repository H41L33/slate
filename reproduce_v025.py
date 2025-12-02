import shutil
from pathlib import Path
from slate.site import Site, Page, Category
from slate.navigation import NavigationGenerator
from slate.render import HTMLRenderer, render_inline_links
from slate.parse import parse_markdown_to_dicts
import re

def test_navbar_paths():
    print("\n--- Testing Navbar Paths ---")
    
    # Mock Site Structure
    # root/
    #   index.html
    #   blog/
    #     post.html
    
    blog_page = Page(Path("blog.md"), Path("blog.html"), {"title": "Blog"}, "blog", True)
    site = Site(
        Path("."),
        Page(Path("index.md"), Path("index.html"), {}, None, False),
        {"blog": Category("blog", blog_page, [])}
    )
    
    # Generate nav for index (root)
    print("Generating nav for Index (root)...")
    nav_index = NavigationGenerator.generate_header_nav(site, current_page=site.index_page)
    print(f"Index Nav: {nav_index}")
    
    # Generate nav for blog post (nested)
    post_page = Page(Path("blog/post.md"), Path("blog/post.html"), {"title": "Post"}, "blog", False)
    
    print("Generating nav for Post (nested)...")
    try:
        nav_post = NavigationGenerator.generate_header_nav(site, current_page=post_page)
        print(f"Post Nav: {nav_post}")
        
        # We expect relative path from blog/post.html to blog.html
        # blog/post.html is in blog/
        # blog.html is in root
        # relative path is ../blog.html
        if '../blog.html' not in nav_post:
             print("FAIL: Nav link does not contain relative path '../blog.html'")
        else:
             print("PASS: Nav link contains relative path")
             
    except Exception as e:
        print(f"Error: {e}")

def test_external_links():
    print("\n--- Testing External Links ---")
    
    # Test cases
    # 1. Raw domain (no protocol) -> Should stay raw (per user "raw" preference)
    # 2. Onion -> Should get http://
    # 3. Gopher -> Should get gopher://
    # 4. WWW -> Should get https://
    
    cases = [
        ("[!EXTERNAL] [about.haileywelsh.me](about.haileywelsh.me)", 'href="about.haileywelsh.me"', "Raw domain stays raw"),
        ("[!EXTERNAL] [Onion](onionurl.onion)", 'href="http://onionurl.onion"', "Onion gets http"),
        ("[!EXTERNAL] [Gopher](hailey.gopher)", 'href="gopher://hailey.gopher"', "Gopher gets gopher://"),
        ("[!EXTERNAL] [WWW](www.google.com)", 'href="https://www.google.com"', "WWW gets https"),
    ]
    
    for text, expected, desc in cases:
        rendered = render_inline_links(text)
        print(f"Input: {text}")
        print(f"Rendered: {rendered}")
        if expected not in rendered:
            print(f"FAIL: {desc} - Expected {expected}")
        else:
            print(f"PASS: {desc}")

def test_callouts():
    print("\n--- Testing Callouts ---")
    # Use paragraph syntax as supported by parser
    md = """[!NOTE]
This is a note."""
    blocks = parse_markdown_to_dicts(md)
    renderer = HTMLRenderer()
    html = renderer.render_blocks(blocks)
    print(f"Rendered: {html}")
    
    if 'class="content-callout callout callout-note"' in html:
        print("PASS: Callout has correct classes")
    else:
        print("FAIL: Missing 'callout' class or incorrect rendering")

if __name__ == "__main__":
    test_navbar_paths()
    test_external_links()
    test_callouts()
    
    # Test CLI Refactor (mocking args)
    print("\n--- Testing CLI Refactor ---")
    import sys
    from slate.main import main
    
    # Mock sys.argv for 'page' command (formerly build)
    print("Testing 'slate page'...")
    try:
        # We need valid input/output for this to run without erroring on file not found
        # Let's just check if it parses correctly and calls handle_page_build
        # We can mock the handler or just catch the error
        pass
    except Exception as e:
        print(f"Page command failed: {e}")
        
    # We will rely on manual verification or pytest for full CLI test
    print("CLI tests deferred to pytest/manual due to complexity of mocking in script.")
