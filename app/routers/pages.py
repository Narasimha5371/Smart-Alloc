from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.template_renderer import render_template
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user_for_pages
from app.models.enums import UserRole
from app.services import notification_service

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
# Prefer `render_template` helper for safe rendering


@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_pages(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return render_template(request, "landing.html")


@router.get("/dashboard")
def dashboard_redirect(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_pages(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Redirect based on role
    role_routes = {
        UserRole.ADMIN: "/admin/dashboard",
        UserRole.HR: "/hr/dashboard",
        UserRole.MANAGER: "/manager/dashboard",
        UserRole.EMPLOYEE: "/employee/dashboard",
        UserRole.CLIENT: "/client/dashboard",
    }
    redirect_url = role_routes.get(user.role, "/login")
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/api/notifications/count")
def notification_count(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_for_pages(request, db)
    if not user:
        return {"count": 0}
    count = notification_service.get_unread_count(db, user.id)
    return {"count": count}
