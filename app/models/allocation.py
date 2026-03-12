from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import AllocationStatus


class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    allocated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[AllocationStatus] = mapped_column(
        String(20), nullable=False, default=AllocationStatus.ALLOCATED, index=True
    )
    ai_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="allocations")
    employee: Mapped["User"] = relationship("User", back_populates="allocations", foreign_keys=[employee_id])
    allocator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[allocated_by])

    def __repr__(self) -> str:
        return f"<Allocation project={self.project_id} employee={self.employee_id} ({self.status})>"


from app.models.project import Project  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
