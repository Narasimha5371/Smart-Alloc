from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.enums import AllocationStatus


class AllocationCreate(BaseModel):
    project_id: int
    employee_id: int
    role_in_project: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("role_in_project")
    @classmethod
    def validate_role_in_project(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v) > 100:
                raise ValueError("Role in project must be no more than 100 characters")
            return v.strip()
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        start_date = info.data.get("start_date")
        if start_date and v and v < start_date:
            raise ValueError("End date must be after start date")
        return v


class AllocationUpdate(BaseModel):
    role_in_project: Optional[str] = None
    status: Optional[AllocationStatus] = None
    progress_percent: Optional[int] = None
    notes: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("role_in_project")
    @classmethod
    def validate_role_in_project(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v) > 100:
                raise ValueError("Role in project must be no more than 100 characters")
            return v.strip()
        return v

    @field_validator("progress_percent")
    @classmethod
    def validate_progress_percent(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Progress percent must be between 0 and 100")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 1000:
            raise ValueError("Notes must be no more than 1000 characters")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        start_date = info.data.get("start_date")
        if start_date and v and v < start_date:
            raise ValueError("End date must be after start date")
        return v


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
