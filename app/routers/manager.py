import json
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.template_renderer import render_template
from sqlalchemy.orm import Session
from app.dependencies import get_db, RoleChecker
from app.models.enums import UserRole, ProjectStatus, AllocationStatus
from app.models.user import User
from app.services import (
    project_service,
    allocation_service,
    user_service,
    notification_service,
)
from app.services.ai_service import suggest_employees
from app.utils.security import generate_csrf_token, validate_csrf_token

router = APIRouter(prefix="/manager", tags=["manager"])
templates = Jinja2Templates(directory="app/templates")
# Prefer `render_template` helper for safe rendering

manager_access = RoleChecker(allowed_roles=[UserRole.MANAGER, UserRole.ADMIN])


@router.get("/dashboard", response_class=HTMLResponse)
def manager_dashboard(
    request: Request,
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    projects = project_service.get_accepted_projects(db)
    return render_template(request, "manager/dashboard.html", {
        "user": user,
        "projects": projects,
        "csrf_token": generate_csrf_token(),
    })


@router.get("/project/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: int,
    request: Request,
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/manager/dashboard", status_code=302)

    allocations = allocation_service.get_allocations_by_project(db, project_id)
    ai_suggestions = [a for a in allocations if a.status == AllocationStatus.SUGGESTED_BY_AI]
    active_allocations = [a for a in allocations if a.status in (AllocationStatus.ALLOCATED, AllocationStatus.ACCEPTED)]

    employees = user_service.get_employees_with_skills(db)

    return render_template(request, "manager/allocate.html", {
        "user": user,
        "project": project,
        "ai_suggestions": ai_suggestions,
        "active_allocations": active_allocations,
        "employees": employees,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/project/{project_id}/ai-suggest")
def trigger_ai_suggestions(
    project_id: int,
    csrf_token: str = Form(...),
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url=f"/manager/project/{project_id}", status_code=302)

    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/manager/dashboard", status_code=302)

    required_skills = [ps.skill.name for ps in project.required_skills if ps.skill]

    # Get all employees with their skills
    employees = user_service.get_employees_with_skills(db)
    candidates = []
    for emp in employees:
        workload = user_service.get_employee_workload(db, emp.id)
        skills = [
            {"name": us.skill.name, "proficiency": us.proficiency_level}
            for us in emp.skills if us.skill
        ]
        candidates.append({
            "id": emp.id,
            "name": emp.full_name,
            "skills": skills,
            "workload_percent": workload,
        })

    suggest_employees(
        db=db,
        project_id=project_id,
        project_title=project.title,
        project_description=project.description,
        required_skills=required_skills,
        candidates=candidates,
    )

    return RedirectResponse(url=f"/manager/project/{project_id}", status_code=302)


@router.post("/project/{project_id}/allocate")
def allocate_employee(
    project_id: int,
    employee_id: int = Form(...),
    role_in_project: str = Form(""),
    csrf_token: str = Form(...),
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url=f"/manager/project/{project_id}", status_code=302)

    project = project_service.get_project_by_id(db, project_id)
    if not project:
        return RedirectResponse(url="/manager/dashboard", status_code=302)

    # Check if already allocated
    existing = allocation_service.get_allocations_by_project(db, project_id)
    already_allocated = any(
        a.employee_id == employee_id and a.status in (AllocationStatus.ALLOCATED, AllocationStatus.ACCEPTED)
        for a in existing
    )

    if not already_allocated:
        # Remove AI suggestion if exists
        for a in existing:
            if a.employee_id == employee_id and a.status == AllocationStatus.SUGGESTED_BY_AI:
                allocation_service.delete_allocation(db, a.id)

        allocation_service.create_allocation(
            db,
            project_id=project_id,
            employee_id=employee_id,
            allocated_by=user.id,
            role_in_project=role_in_project or None,
            start_date=project.deadline,
        )

        # Update project status to IN_PROGRESS
        if project.status == ProjectStatus.ACCEPTED:
            project_service.update_project_status(db, project_id, ProjectStatus.IN_PROGRESS)

        # Notify employee
        notification_service.create_notification(
            db,
            user_id=employee_id,
            title="New Project Assignment",
            message=f'You have been assigned to project "{project.title}"' +
                    (f' as {role_in_project}' if role_in_project else '') + '.',
            link=f"/employee/dashboard",
        )

    return RedirectResponse(url=f"/manager/project/{project_id}", status_code=302)


@router.post("/allocation/{allocation_id}/remove")
def remove_allocation(
    allocation_id: int,
    csrf_token: str = Form(...),
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/manager/dashboard", status_code=302)

    allocation = allocation_service.get_allocation_by_id(db, allocation_id)
    if allocation:
        project_id = allocation.project_id
        allocation_service.delete_allocation(db, allocation_id)
        return RedirectResponse(url=f"/manager/project/{project_id}", status_code=302)
    return RedirectResponse(url="/manager/dashboard", status_code=302)


@router.get("/progress", response_class=HTMLResponse)
def progress_overview(
    request: Request,
    user: User = Depends(manager_access),
    db: Session = Depends(get_db),
):
    projects = project_service.get_projects(db, status=ProjectStatus.IN_PROGRESS)
    project_data = []
    for p in projects:
        allocations = allocation_service.get_allocations_by_project(db, p.id)
        active = [a for a in allocations if a.status in (AllocationStatus.ALLOCATED, AllocationStatus.ACCEPTED, AllocationStatus.COMPLETED)]
        avg_progress = sum(a.progress_percent for a in active) / len(active) if active else 0
        project_data.append({
            "project": p,
            "allocations": active,
            "avg_progress": round(avg_progress),
        })

    return render_template(request, "manager/progress.html", {
        "user": user,
        "project_data": project_data,
    })
