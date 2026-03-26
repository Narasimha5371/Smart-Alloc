from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.enums import ProjectStatus, Priority


class ProjectCreate(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    deadline: Optional[date] = None
    budget: Optional[float] = None
    skill_ids: List[int] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long")
        if len(v) > 255:
            raise ValueError("Title must be no more than 255 characters")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip()

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Budget cannot be negative")
        return v


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    deadline: Optional[date] = None
    budget: Optional[float] = None
    status: Optional[ProjectStatus] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 3:
                raise ValueError("Title must be at least 3 characters long")
            if len(v) > 255:
                raise ValueError("Title must be no more than 255 characters")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Budget cannot be negative")
        return v


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    client_id: int
    status: ProjectStatus
    priority: Priority
    deadline: Optional[date] = None
    budget: Optional[float] = None
    ai_recommendation: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    reviewed_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
