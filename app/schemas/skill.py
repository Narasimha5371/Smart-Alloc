from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillCreate(BaseModel):
    name: str
    category: Optional[str] = None


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None


class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = 3  # 1-5 scale


class UserSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    skill_id: int
    proficiency_level: int


class ProjectSkillCreate(BaseModel):
    skill_id: int
    importance_level: int = 3  # 1-5 scale
