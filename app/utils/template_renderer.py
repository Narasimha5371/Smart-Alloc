from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi.responses import HTMLResponse
from typing import Dict, Any

TEMPLATE_DIR = "app/templates"


def render_template(request, template_name: str, context: Dict[str, Any] | None = None, status_code: int = 200) -> HTMLResponse:
    ctx = dict(context or {})
    # Ensure request is available to templates
    ctx.setdefault("request", request)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)
    content = template.render(ctx)
    return HTMLResponse(content, status_code=status_code)
