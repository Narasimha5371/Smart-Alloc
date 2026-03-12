import json
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db, RoleChecker
from app.models.enums import UserRole, ProjectStatus
from app.models.user import User
from app.models.skill import Skill
from app.services import (
    project_service,
    user_service,
    import_service,
    notification_service,
)
from app.services.ai_service import evaluate_project
from app.utils.security import generate_csrf_token, validate_csrf_token

router = APIRouter(prefix="/hr", tags=["hr"])
templates = Jinja2Templates(directory="app/templates")

hr_access = RoleChecker(allowed_roles=[UserRole.HR, UserRole.ADMIN])


@router.get("/dashboard", response_class=HTMLResponse)
def hr_dashboard(
    request: Request,
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    pending_projects = project_service.get_projects(db, status=ProjectStatus.PENDING)
    reviewed_projects = project_service.get_projects(db, status=ProjectStatus.AI_REVIEWED)
    all_projects = project_service.get_projects(db)
    employees = user_service.get_employees(db)
    return templates.TemplateResponse("hr/dashboard.html", {
        "request": request,
        "user": user,
        "pending_projects": pending_projects,
        "reviewed_projects": reviewed_projects,
        "all_projects": all_projects,
        "employees": employees,
        "csrf_token": generate_csrf_token(),
    })


@router.get("/project/{project_id}", response_class=HTMLResponse)
def project_review(
    project_id: int,
    request: Request,
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/hr/dashboard", status_code=302)

    ai_data = None
    if project.ai_recommendation:
        try:
            ai_data = json.loads(project.ai_recommendation)
        except json.JSONDecodeError:
            ai_data = {"reasoning": project.ai_recommendation}

    return templates.TemplateResponse("hr/project_review.html", {
        "request": request,
        "user": user,
        "project": project,
        "ai_data": ai_data,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/project/{project_id}/ai-review")
def trigger_ai_review(
    project_id: int,
    request: Request,
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/hr/dashboard", status_code=302)

    # Gather context for AI
    employee_count = user_service.get_user_count_by_role(db, UserRole.EMPLOYEE)
    all_skills = db.query(Skill).all()
    available_skills = [s.name for s in all_skills]
    active_project_count = project_service.get_project_count_by_status(db, ProjectStatus.IN_PROGRESS)

    required_skills = [ps.skill.name for ps in project.required_skills if ps.skill]

    result = evaluate_project(
        project_title=project.title,
        project_description=project.description,
        project_deadline=str(project.deadline) if project.deadline else None,
        project_budget=project.budget,
        required_skills=required_skills,
        employee_count=employee_count,
        available_skills=available_skills,
        active_project_count=active_project_count,
    )

    project_service.update_project_status(
        db,
        project_id,
        status=ProjectStatus.AI_REVIEWED,
        ai_recommendation=json.dumps(result),
        ai_confidence_score=result.get("confidence", 0.0),
    )

    return RedirectResponse(url=f"/hr/project/{project_id}", status_code=302)


@router.post("/project/{project_id}/decide")
def decide_project(
    project_id: int,
    decision: str = Form(...),
    csrf_token: str = Form(...),
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url=f"/hr/project/{project_id}", status_code=302)

    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/hr/dashboard", status_code=302)

    new_status = ProjectStatus.ACCEPTED if decision == "accept" else ProjectStatus.REJECTED
    project_service.update_project_status(db, project_id, new_status, reviewed_by=user.id)

    # Notify the client
    notification_service.create_notification(
        db,
        user_id=project.client_id,
        title=f"Project {new_status.value.replace('_', ' ').title()}",
        message=f'Your project "{project.title}" has been {new_status.value}.',
        link=f"/client/project/{project_id}",
    )

    return RedirectResponse(url="/hr/dashboard", status_code=302)


@router.get("/employees", response_class=HTMLResponse)
def employees_page(
    request: Request,
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    employees = user_service.get_employees_with_skills(db)
    return templates.TemplateResponse("hr/employees.html", {
        "request": request,
        "user": user,
        "employees": employees,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/employees/upload")
def upload_employees(
    request: Request,
    file: UploadFile = File(...),
    csrf_token: str = Form(...),
    user: User = Depends(hr_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/hr/employees", status_code=302)

    content = file.file.read()
    result = import_service.process_upload(db, file.filename or "", content)

    return templates.TemplateResponse("hr/upload_result.html", {
        "request": request,
        "user": user,
        "result": result,
    })
