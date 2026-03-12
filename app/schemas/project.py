from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import ProjectStatus, Priority


class ProjectCreate(BaseModel):
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    deadline: Optional[date] = None
    budget: Optional[float] = None
    skill_ids: List[int] = []


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    deadline: Optional[date] = None
    budget: Optional[float] = None
    status: Optional[ProjectStatus] = None


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
