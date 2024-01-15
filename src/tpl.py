from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
)


def get_template(template_name: str) -> Template:
    return env.get_template(template_name)


def render(tpl: str, **kwargs: Any) -> str:
    template = get_template("messages/" + tpl + ".txt")
    return template.render(**kwargs)


__all__ = [
    "get_template",
    "render",
]
