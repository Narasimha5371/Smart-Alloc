from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    users: Mapped[List["UserSkill"]] = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")
    projects: Mapped[List["ProjectSkill"]] = relationship("ProjectSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Skill {self.name}>"


class UserSkill(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5 scale

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="users")

    def __repr__(self) -> str:
        return f"<UserSkill user={self.user_id} skill={self.skill_id} level={self.proficiency_level}>"


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    importance_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5 scale

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="required_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="projects")

    def __repr__(self) -> str:
        return f"<ProjectSkill project={self.project_id} skill={self.skill_id}>"


# For relationship resolution
from app.models.user import User  # noqa: E402, F401
from app.models.project import Project  # noqa: E402, F401
