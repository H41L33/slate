import unittest
from slate.render import HTMLRenderer, VariableRegistry, CustomTokenRegistry, render_inline_links

class TestFeatures(unittest.TestCase):
    def test_button_token(self):
        """Test [!BUTTON] token rendering."""
        text = "Click [!BUTTON] [Here](https://example.com)"
        expected = 'Click <button class="content-button" onclick="window.location.href=\'https://example.com\'">Here</button>'
        self.assertEqual(render_inline_links(text), expected)

    def test_variable_registry_default(self):
        """Test default variables in VariableRegistry."""
        renderer = HTMLRenderer()
        renderer.date = "01/01/2025"
        renderer.time = "12:00"
        
        text = "Date: {{date}}, Time: {{time}}"
        expected = "Date: 01/01/2025, Time: 12:00"
        self.assertEqual(renderer._apply_dt(text), expected)

    def test_variable_registry_custom(self):
        """Test adding a custom variable to VariableRegistry."""
        VariableRegistry.register("custom-var", lambda c: "Custom Value")
        
        renderer = HTMLRenderer()
        text = "Value: {{custom-var}}"
        expected = "Value: Custom Value"
        self.assertEqual(renderer._apply_dt(text), expected)

    def test_variable_registry_context(self):
        """Test that context is passed correctly to handlers."""
        VariableRegistry.register("title-echo", lambda c: f"Title: {c.get('title')}")
        
        renderer = HTMLRenderer()
        renderer.title = "My Page"
        
        text = "{{title-echo}}"
        expected = "Title: My Page"
        self.assertEqual(renderer._apply_dt(text), expected)

if __name__ == '__main__':
    unittest.main()
