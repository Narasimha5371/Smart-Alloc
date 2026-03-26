from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, AnyHttpUrl
from app.models.enums import NotificationType


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: NotificationType = NotificationType.SYSTEM
    link: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError("Title is required")
        if len(v) > 255:
            raise ValueError("Title must be no more than 255 characters")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or len(v.strip()) < 1:
            raise ValueError("Message is required")
        if len(v) > 1000:
            raise ValueError("Message must be no more than 1000 characters")
        return v.strip()

    @field_validator("link")
    @classmethod
    def validate_link(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) == 0:
                return None
            # Basic URL validation
            if not (v.startswith("http://") or v.startswith("https://")):
                raise ValueError("Link must be a valid URL starting with http:// or https://")
            if len(v) > 500:
                raise ValueError("Link must be no more than 500 characters")
            return v.strip()
        return v


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    link: Optional[str] = None
    created_at: datetime
