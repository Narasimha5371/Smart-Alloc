from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.user import User
from app.models.skill import UserSkill, Skill
from app.models.allocation import Allocation
from app.models.enums import UserRole, AllocationStatus
from app.utils.security import get_password_hash


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def get_all_users(db: Session, role: Optional[UserRole] = None, skip: int = 0, limit: int = 100) -> List[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()


def get_employees(db: Session) -> List[User]:
    return db.query(User).filter(User.role == UserRole.EMPLOYEE, User.is_active == True).all()


def get_employees_with_skills(db: Session) -> List[User]:
    return (
        db.query(User)
        .filter(User.role == UserRole.EMPLOYEE, User.is_active == True)
        .options(joinedload(User.skills).joinedload(UserSkill.skill))
        .all()
    )


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def create_user(
    db: Session,
    email: str,
    full_name: str,
    password: str,
    role: UserRole,
    department: Optional[str] = None,
) -> User:
    user = User(
        email=email.lower().strip(),
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        department=department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_employee_workload(db: Session, employee_id: int) -> float:
    """Returns the current workload as percentage (0-100) based on active allocations."""
    active_allocations = (
        db.query(Allocation)
        .filter(
            Allocation.employee_id == employee_id,
            Allocation.status.in_([AllocationStatus.ALLOCATED, AllocationStatus.ACCEPTED]),
        )
        .count()
    )
    # Simple model: each allocation = 25% workload, cap at 100%
    return min(active_allocations * 25.0, 100.0)


def get_employees_by_skill_ids(db: Session, skill_ids: List[int]) -> List[User]:
    """Get employees who have at least one of the specified skills."""
    if not skill_ids:
        return get_employees(db)

    return (
        db.query(User)
        .join(UserSkill)
        .filter(
            User.role == UserRole.EMPLOYEE,
            User.is_active == True,
            UserSkill.skill_id.in_(skill_ids),
        )
        .options(joinedload(User.skills).joinedload(UserSkill.skill))
        .distinct()
        .all()
    )


def get_user_count(db: Session) -> int:
    return db.query(func.count(User.id)).scalar()


def get_user_count_by_role(db: Session, role: UserRole) -> int:
    return db.query(func.count(User.id)).filter(User.role == role).scalar()
