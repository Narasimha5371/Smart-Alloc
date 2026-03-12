from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import AllocationStatus


class AllocationCreate(BaseModel):
    project_id: int
    employee_id: int
    role_in_project: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AllocationUpdate(BaseModel):
    role_in_project: Optional[str] = None
    status: Optional[AllocationStatus] = None
    progress_percent: Optional[int] = None
    notes: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    employee_id: int
    role_in_project: Optional[str] = None
    allocated_by: Optional[int] = None
    status: AllocationStatus
    ai_match_score: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress_percent: int
    notes: Optional[str] = None
