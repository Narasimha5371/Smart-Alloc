import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CLIENT = "client"


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    AI_REVIEWED = "ai_reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AllocationStatus(str, enum.Enum):
    SUGGESTED_BY_AI = "suggested_by_ai"
    ALLOCATED = "allocated"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, enum.Enum):
    ALLOCATION = "allocation"
    PROJECT_UPDATE = "project_update"
    SYSTEM = "system"
    AI_SUGGESTION = "ai_suggestion"
