from typing import List
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db, RoleChecker
from app.models.enums import UserRole, ProjectStatus, Priority
from app.models.user import User
from app.models.skill import Skill
from app.services import project_service, notification_service
from app.utils.security import generate_csrf_token, validate_csrf_token

router = APIRouter(prefix="/client", tags=["client"])
templates = Jinja2Templates(directory="app/templates")

client_access = RoleChecker(allowed_roles=[UserRole.CLIENT, UserRole.ADMIN])


@router.get("/dashboard", response_class=HTMLResponse)
def client_dashboard(
    request: Request,
    user: User = Depends(client_access),
    db: Session = Depends(get_db),
):
    projects = project_service.get_projects(db, client_id=user.id)
    unread_count = notification_service.get_unread_count(db, user.id)

    return templates.TemplateResponse("client/dashboard.html", {
        "request": request,
        "user": user,
        "projects": projects,
        "unread_count": unread_count,
    })


@router.get("/submit", response_class=HTMLResponse)
def submit_project_page(
    request: Request,
    user: User = Depends(client_access),
    db: Session = Depends(get_db),
):
    skills = db.query(Skill).order_by(Skill.name).all()
    return templates.TemplateResponse("client/submit_project.html", {
        "request": request,
        "user": user,
        "skills": skills,
        "csrf_token": generate_csrf_token(),
        "priorities": [p for p in Priority],
    })


@router.post("/submit")
def submit_project(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form("medium"),
    deadline: str = Form(""),
    budget: str = Form(""),
    csrf_token: str = Form(...),
    skill_ids: List[str] = Form(default=[]),
    user: User = Depends(client_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/client/submit", status_code=302)

    parsed_skill_ids = [int(s) for s in skill_ids if s]

    from datetime import date as date_type
    deadline_date = None
    if deadline:
        try:
            deadline_date = date_type.fromisoformat(deadline)
        except ValueError:
            pass

    budget_float = None
    if budget:
        try:
            budget_float = float(budget)
        except ValueError:
            pass

    project = project_service.create_project(
        db,
        title=title,
        description=description,
        client_id=user.id,
        priority=Priority(priority),
        deadline=deadline_date,
        budget=budget_float,
        skill_ids=parsed_skill_ids,
    )

    return RedirectResponse(url="/client/dashboard", status_code=302)


@router.get("/project/{project_id}", response_class=HTMLResponse)
def view_project(
    project_id: int,
    request: Request,
    user: User = Depends(client_access),
    db: Session = Depends(get_db),
):
    project = project_service.get_project_by_id(db, project_id)
    if not project or project.client_id != user.id:
        return RedirectResponse(url="/client/dashboard", status_code=302)

    return templates.TemplateResponse("client/project_detail.html", {
        "request": request,
        "user": user,
        "project": project,
    })
