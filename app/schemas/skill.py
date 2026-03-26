from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class SkillCreate(BaseModel):
    name: str
    category: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError("Skill name is required")
        if len(v) > 100:
            raise ValueError("Skill name must be no more than 100 characters")
        return v.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                return None
            if len(v) > 50:
                raise ValueError("Category must be no more than 50 characters")
            return v.strip()
        return v


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None


class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = 3  # 1-5 scale

    @field_validator("proficiency_level")
    @classmethod
    def validate_proficiency_level(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Proficiency level must be between 1 and 5")
        return v


class UserSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    skill_id: int
    proficiency_level: int


class ProjectSkillCreate(BaseModel):
    skill_id: int
    importance_level: int = 3  # 1-5 scale

    @field_validator("importance_level")
    @classmethod
    def validate_importance_level(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Importance level must be between 1 and 5")
        return v
