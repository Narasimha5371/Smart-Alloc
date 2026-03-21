from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.dependencies import get_db, RoleChecker
from app.models.enums import UserRole
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.services import allocation_service, notification_service
from app.utils.security import generate_csrf_token, validate_csrf_token

router = APIRouter(prefix="/employee", tags=["employee"])
templates = Jinja2Templates(directory="app/templates")

employee_access = RoleChecker(allowed_roles=[UserRole.EMPLOYEE, UserRole.ADMIN])


@router.get("/dashboard", response_class=HTMLResponse)
def employee_dashboard(
    request: Request,
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    allocations = allocation_service.get_allocations_by_employee(db, user.id)
    notifications = notification_service.get_notifications_for_user(db, user.id, unread_only=True)
    unread_count = notification_service.get_unread_count(db, user.id)

    return templates.TemplateResponse("employee/dashboard.html", {
        "request": request,
        "user": user,
        "allocations": allocations,
        "notifications": notifications,
        "unread_count": unread_count,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/allocation/{allocation_id}/progress")
def update_progress(
    allocation_id: int,
    progress: int = Form(...),
    notes: str = Form(""),
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/dashboard", status_code=302)

    allocation = allocation_service.get_allocation_by_id(db, allocation_id)
    if allocation and allocation.employee_id == user.id:
        allocation_service.update_progress(db, allocation_id, progress, notes or None)

    return RedirectResponse(url="/employee/dashboard", status_code=302)


@router.get("/skills", response_class=HTMLResponse)
def skills_page(
    request: Request,
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    all_skills = db.query(Skill).order_by(Skill.name).all()
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user.id).all()
    user_skill_ids = {us.skill_id for us in user_skills}
    user_skill_map = {us.skill_id: us for us in user_skills}

    return templates.TemplateResponse("employee/skills.html", {
        "request": request,
        "user": user,
        "all_skills": all_skills,
        "user_skill_ids": user_skill_ids,
        "user_skill_map": user_skill_map,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/skills/add")
def add_skill(
    skill_id: int = Form(0),
    new_skill_name: str = Form(""),
    proficiency_level: int = Form(3),
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/skills", status_code=302)

    # Create new skill if name is provided and skill_id is 0
    if not skill_id and new_skill_name.strip():
        existing = db.query(Skill).filter(Skill.name == new_skill_name.strip()).first()
        if existing:
            skill_id = existing.id
        else:
            new_skill = Skill(name=new_skill_name.strip())
            db.add(new_skill)
            db.flush()
            skill_id = new_skill.id

    if skill_id:
        # Check if user already has this skill
        existing_us = db.query(UserSkill).filter(
            UserSkill.user_id == user.id, UserSkill.skill_id == skill_id
        ).first()
        if not existing_us:
            user_skill = UserSkill(
                user_id=user.id,
                skill_id=skill_id,
                proficiency_level=max(1, min(5, proficiency_level)),
            )
            db.add(user_skill)
            db.commit()

    return RedirectResponse(url="/employee/skills", status_code=302)


@router.post("/skills/{user_skill_id}/update")
def update_skill_proficiency(
    user_skill_id: int,
    proficiency_level: int = Form(...),
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/skills", status_code=302)

    us = db.query(UserSkill).filter(
        UserSkill.id == user_skill_id, UserSkill.user_id == user.id
    ).first()
    if us:
        us.proficiency_level = max(1, min(5, proficiency_level))
        db.commit()
    return RedirectResponse(url="/employee/skills", status_code=302)


@router.post("/skills/{user_skill_id}/remove")
def remove_skill(
    user_skill_id: int,
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/skills", status_code=302)

    us = db.query(UserSkill).filter(
        UserSkill.id == user_skill_id, UserSkill.user_id == user.id
    ).first()
    if us:
        db.delete(us)
        db.commit()
    return RedirectResponse(url="/employee/skills", status_code=302)


@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(
    request: Request,
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    notifications = notification_service.get_notifications_for_user(db, user.id)
    return templates.TemplateResponse("employee/notifications.html", {
        "request": request,
        "user": user,
        "notifications": notifications,
        "csrf_token": generate_csrf_token(),
    })


@router.post("/notifications/{notification_id}/read")
def mark_read(
    notification_id: int,
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/notifications", status_code=302)

    notification_service.mark_as_read(db, notification_id, user.id)
    return RedirectResponse(url="/employee/notifications", status_code=302)


@router.post("/notifications/read-all")
def mark_all_read(
    csrf_token: str = Form(...),
    user: User = Depends(employee_access),
    db: Session = Depends(get_db),
):
    if not validate_csrf_token(csrf_token):
        return RedirectResponse(url="/employee/notifications", status_code=302)

    notification_service.mark_all_as_read(db, user.id)
    return RedirectResponse(url="/employee/notifications", status_code=302)
