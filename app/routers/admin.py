from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_login, RoleChecker
from app.models.enums import UserRole, ProjectStatus, AllocationStatus
from app.models.user import User
from app.services import user_service, project_service, allocation_service
from app.utils.security import generate_csrf_token, validate_csrf_token, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

admin_only = RoleChecker(allowed_roles=[UserRole.ADMIN])


@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(
    request: Request,
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    stats = {
        "total_users": user_service.get_user_count(db),
        "total_employees": user_service.get_user_count_by_role(db, UserRole.EMPLOYEE),
        "total_projects": project_service.get_project_count(db),
        "pending_projects": project_service.get_project_count_by_status(db, ProjectStatus.PENDING),
        "active_projects": project_service.get_project_count_by_status(db, ProjectStatus.IN_PROGRESS),
        "active_allocations": allocation_service.get_active_allocation_count(db),
    }
    users = user_service.get_all_users(db)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "users": users,
        "csrf_token": generate_csrf_token(),
    })


@router.get("/users", response_class=HTMLResponse)
def admin_users(
    request: Request,
    role: str = None,
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    users = user_service.get_all_users(db)
    if role:
        try:
            filtered_role = UserRole(role)
            users = [u for u in users if u.role == filtered_role]
        except ValueError:
            pass  # Ignore invalid role filters

    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "user": user,
        "users": users,
        "current_role_filter": role,
        "csrf_token": generate_csrf_token(),
    })


@router.get("/projects", response_class=HTMLResponse)
def admin_projects(
    request: Request,
    status: str = None,
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    if status:
        try:
            filtered_status = ProjectStatus(status)
            projects = project_service.get_projects(db, status=filtered_status)
        except ValueError:
            projects = project_service.get_projects(db)
    else:
        projects = project_service.get_projects(db)

    return templates.TemplateResponse("admin/projects.html", {
        "request": request,
        "user": user,
        "projects": projects,
        "current_status_filter": status,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/users/create")
def create_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    department: str = Form(""),
    csrf_token: str = Form(...),
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/admin/dashboard", status_code=302)

    try:
        user_role = UserRole(role)
        user_service.create_user(
            db, email, full_name, password, user_role, department or None
        )
    except Exception:
        pass  # Silently handle — redirect back

    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.post("/users/{user_id}/toggle")
def toggle_user(
    user_id: int,
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    target = user_service.get_user_by_id(db, user_id)
    if target and target.id != user.id:
        user_service.update_user(db, user_id, is_active=not target.is_active)
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.post("/users/{user_id}/delete")
def delete_user(
    user_id: int,
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    if user_id != user.id:
        user_service.delete_user(db, user_id)
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.post("/users/{user_id}/update-role")
def update_user_role(
    user_id: int,
    role: str = Form(...),
    user: User = Depends(admin_only),
    db: Session = Depends(get_db),
):
    try:
        user_role = UserRole(role)
        user_service.update_user(db, user_id, role=user_role)
    except Exception:
        pass
    return RedirectResponse(url="/admin/dashboard", status_code=302)
