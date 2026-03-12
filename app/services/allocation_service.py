from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.allocation import Allocation
from app.models.project import Project
from app.models.user import User
from app.models.enums import AllocationStatus


def create_allocation(
    db: Session,
    project_id: int,
    employee_id: int,
    allocated_by: int,
    role_in_project: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    ai_match_score: Optional[float] = None,
    status: AllocationStatus = AllocationStatus.ALLOCATED,
) -> Allocation:
    allocation = Allocation(
        project_id=project_id,
        employee_id=employee_id,
        allocated_by=allocated_by,
        role_in_project=role_in_project,
        start_date=start_date,
        end_date=end_date,
        ai_match_score=ai_match_score,
        status=status,
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation


def get_allocation_by_id(db: Session, allocation_id: int) -> Optional[Allocation]:
    return (
        db.query(Allocation)
        .options(joinedload(Allocation.project), joinedload(Allocation.employee))
        .filter(Allocation.id == allocation_id)
        .first()
    )


def get_allocations_by_project(db: Session, project_id: int) -> List[Allocation]:
    return (
        db.query(Allocation)
        .options(joinedload(Allocation.employee))
        .filter(Allocation.project_id == project_id)
        .order_by(Allocation.ai_match_score.desc().nullslast())
        .all()
    )


def get_allocations_by_employee(db: Session, employee_id: int) -> List[Allocation]:
    return (
        db.query(Allocation)
        .options(joinedload(Allocation.project))
        .filter(Allocation.employee_id == employee_id)
        .order_by(Allocation.created_at.desc())
        .all()
    )


def update_allocation(db: Session, allocation_id: int, **kwargs) -> Optional[Allocation]:
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(allocation, key):
            setattr(allocation, key, value)
    db.commit()
    db.refresh(allocation)
    return allocation


def update_progress(db: Session, allocation_id: int, progress_percent: int, notes: Optional[str] = None) -> Optional[Allocation]:
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        return None
    allocation.progress_percent = max(0, min(100, progress_percent))
    if notes:
        allocation.notes = notes
    if progress_percent >= 100:
        allocation.status = AllocationStatus.COMPLETED
    db.commit()
    db.refresh(allocation)
    return allocation


def delete_allocation(db: Session, allocation_id: int) -> bool:
    allocation = db.query(Allocation).filter(Allocation.id == allocation_id).first()
    if not allocation:
        return False
    db.delete(allocation)
    db.commit()
    return True


def get_active_allocation_count(db: Session) -> int:
    return (
        db.query(func.count(Allocation.id))
        .filter(Allocation.status.in_([AllocationStatus.ALLOCATED, AllocationStatus.ACCEPTED]))
        .scalar()
    )


def remove_ai_suggestions_for_project(db: Session, project_id: int):
    """Remove all AI-suggested (not yet allocated) allocations for a project."""
    db.query(Allocation).filter(
        Allocation.project_id == project_id,
        Allocation.status == AllocationStatus.SUGGESTED_BY_AI,
    ).delete()
    db.commit()
