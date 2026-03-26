from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import logging
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.utils.template_renderer import render_template
from app.config import get_settings
from app.database import engine, Base

# Import all models so tables are created
from app.models import (  # noqa: F401
    User, Skill, UserSkill, ProjectSkill,
    Project, Allocation, Notification,
)

settings = get_settings()

# Configure basic logging so unhandled exceptions are recorded
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")
# Prefer `render_template` helper for safe rendering in handlers

# Create tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# --- Include Routers ---
from app.routers import auth, admin, hr, manager, employee, client, pages  # noqa: E402

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(hr.router)
app.include_router(manager.router)
app.include_router(employee.router)
app.include_router(client.router)


# --- Error Handlers ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return render_template(request, "errors/404.html", status_code=404)


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return render_template(request, "errors/403.html", status_code=403)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    # Log full traceback for diagnostics and attach a short correlation id
    correlation_id = uuid.uuid4().hex[:8]
    logging.exception("Unhandled exception (cid=%s) while handling request %s", correlation_id, request.url)
    return render_template(request, "errors/500.html", {"correlation_id": correlation_id}, status_code=500)
