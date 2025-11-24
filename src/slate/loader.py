import os

from jinja2 import Environment, FileSystemLoader


def load_markdown(md_path: str) -> str:
    with open(md_path, encoding="utf-8") as f:
        return f.read()
    
def load_template(template_path: str):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    return env.get_template(os.path.basename(template_path))