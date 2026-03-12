from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.EMPLOYEE, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    allocations: Mapped[List["Allocation"]] = relationship(
        "Allocation", back_populates="employee", foreign_keys="[Allocation.employee_id]"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    submitted_projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="client", foreign_keys="[Project.client_id]"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


# Import here to avoid circular imports — these are needed for relationship resolution
from app.models.skill import UserSkill  # noqa: E402, F401
from app.models.allocation import Allocation  # noqa: E402, F401
from app.models.notification import Notification  # noqa: E402, F401
from app.models.project import Project  # noqa: E402, F401
