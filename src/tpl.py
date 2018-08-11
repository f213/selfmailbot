from os.path import dirname, join

from jinja2 import Environment, FileSystemLoader, Template

env = Environment(
    loader=FileSystemLoader(join(dirname(__file__), 'templates')),
)


def get_template(template_name: str) -> Template:
    return env.get_template(template_name)


__all__ = [
    get_template,
]
