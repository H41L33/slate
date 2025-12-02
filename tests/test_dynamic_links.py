import unittest

from slate.render import CustomTokenRegistry, render_inline_links


class TestDynamicLinks(unittest.TestCase):
    def test_md_page_link_conversion(self):
        # Test basic conversion
        text = "[!MD-PAGE] [My Post](posts/post1.md)"
        expected = '<a href="posts/post1.html" class="content-link">My Post</a>'
        self.assertEqual(render_inline_links(text), expected)

    def test_md_page_link_case_insensitive(self):
        # Test case insensitivity for extension
        text = "[!MD-PAGE] [My Post](posts/post1.MD)"
        expected = '<a href="posts/post1.html" class="content-link">My Post</a>'
        self.assertEqual(render_inline_links(text), expected)

    def test_md_page_link_no_extension_change(self):
        # Test link without .md extension (should remain as is, just wrapped)
        text = "[!MD-PAGE] [My Post](posts/post1.html)"
        expected = '<a href="posts/post1.html" class="content-link">My Post</a>'
        self.assertEqual(render_inline_links(text), expected)

    def test_standard_link_untouched(self):
        # Test standard link is converted to html
        text = "[My Post](posts/post1.md)"
        expected = '<a href="posts/post1.html" class="content-link">My Post</a>'
        self.assertEqual(render_inline_links(text), expected)

    def test_mixed_links(self):
        # Test mixed content
        text = "Check out [!MD-PAGE] [Post 1](p1.md) and [Post 2](p2.md)"
        expected = 'Check out <a href="p1.html" class="content-link">Post 1</a> and <a href="p2.html" class="content-link">Post 2</a>'
        self.assertEqual(render_inline_links(text), expected)

    def test_custom_token_extensibility(self):
        # Define a custom handler
        def custom_handler(match):
            label = match.group("label")
            href = match.group("href")
            return f'<button onclick="location.href=\'{href}\'">{label}</button>'
        
        # Register it
        CustomTokenRegistry.register("TEST-BUTTON", custom_handler)
        
        # Test it
        text = "[!TEST-BUTTON] [Click Me](page.html)"
        expected = '<button onclick="location.href=\'page.html\'">Click Me</button>'
        self.assertEqual(render_inline_links(text), expected)

    def test_unknown_token_ignored(self):
        # Test that unknown tokens are ignored but the link part is still rendered by standard link logic
        text = "[!UNKNOWN] [Label](href)"
        # The custom token regex matches, handler returns it as is.
        # Then the standard link regex matches [Label](href) and converts it.
        expected = '[!UNKNOWN] <a href="href" class="content-link">Label</a>'
        self.assertEqual(render_inline_links(text), expected)

if __name__ == '__main__':
    unittest.main()
