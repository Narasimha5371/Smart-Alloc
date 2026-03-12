from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.enums import UserRole
from app.utils.security import verify_password, get_password_hash, create_access_token


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def register_user(
    db: Session,
    email: str,
    full_name: str,
    password: str,
    role: UserRole = UserRole.EMPLOYEE,
    department: Optional[str] = None,
) -> User:
    # Check if email already exists
    existing = db.query(User).filter(User.email == email.lower().strip()).first()
    if existing:
        raise ValueError("Email already registered")

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


def create_token_for_user(user: User) -> str:
    return create_access_token(data={"sub": str(user.id), "role": str(user.role)})
