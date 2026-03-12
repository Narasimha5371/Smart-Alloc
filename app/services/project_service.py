from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.project import Project
from app.models.skill import ProjectSkill
from app.models.enums import ProjectStatus, Priority


def create_project(
    db: Session,
    title: str,
    description: str,
    client_id: int,
    priority: Priority = Priority.MEDIUM,
    deadline: Optional[date] = None,
    budget: Optional[float] = None,
    skill_ids: List[int] = None,
) -> Project:
    project = Project(
        title=title,
        description=description,
        client_id=client_id,
        priority=priority,
        deadline=deadline,
        budget=budget,
    )
    db.add(project)
    db.flush()  # Get the project ID

    if skill_ids:
        for skill_id in skill_ids:
            ps = ProjectSkill(project_id=project.id, skill_id=skill_id)
            db.add(ps)

    db.commit()
    db.refresh(project)
    return project


def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    return (
        db.query(Project)
        .options(
            joinedload(Project.required_skills).joinedload(ProjectSkill.skill),
            joinedload(Project.client),
            joinedload(Project.allocations),
        )
        .filter(Project.id == project_id)
        .first()
    )


def get_projects(
    db: Session,
    status: Optional[ProjectStatus] = None,
    client_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Project]:
    query = db.query(Project).options(joinedload(Project.client))
    if status:
        query = query.filter(Project.status == status)
    if client_id:
        query = query.filter(Project.client_id == client_id)
    return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def get_pending_projects(db: Session) -> List[Project]:
    return get_projects(db, status=ProjectStatus.PENDING)


def get_accepted_projects(db: Session) -> List[Project]:
    return (
        db.query(Project)
        .options(
            joinedload(Project.client),
            joinedload(Project.required_skills).joinedload(ProjectSkill.skill),
            joinedload(Project.allocations),
        )
        .filter(Project.status.in_([ProjectStatus.ACCEPTED, ProjectStatus.IN_PROGRESS]))
        .order_by(Project.created_at.desc())
        .all()
    )


def update_project_status(
    db: Session,
    project_id: int,
    status: ProjectStatus,
    reviewed_by: Optional[int] = None,
    ai_recommendation: Optional[str] = None,
    ai_confidence_score: Optional[float] = None,
) -> Optional[Project]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    project.status = status
    if reviewed_by:
        project.reviewed_by = reviewed_by
    if ai_recommendation:
        project.ai_recommendation = ai_recommendation
    if ai_confidence_score is not None:
        project.ai_confidence_score = ai_confidence_score
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, **kwargs) -> Optional[Project]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(project, key):
            setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def get_project_count(db: Session) -> int:
    return db.query(func.count(Project.id)).scalar()


def get_project_count_by_status(db: Session, status: ProjectStatus) -> int:
    return db.query(func.count(Project.id)).filter(Project.status == status).scalar()
