from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import get_settings
from app.database import engine, Base

# Import all models so tables are created
from app.models import (  # noqa: F401
    User, Skill, UserSkill, ProjectSkill,
    Project, Allocation, Notification,
)

settings = get_settings()

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
    return templates.TemplateResponse("errors/404.html", {
        "request": request,
    }, status_code=404)


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return templates.TemplateResponse("errors/403.html", {
        "request": request,
    }, status_code=403)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse("errors/500.html", {
        "request": request,
    }, status_code=500)
