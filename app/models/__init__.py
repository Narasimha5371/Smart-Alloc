# Re-export all models so Alembic and table creation discover them
from app.models.enums import UserRole, ProjectStatus, AllocationStatus, Priority, NotificationType  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.skill import Skill, UserSkill, ProjectSkill  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.allocation import Allocation  # noqa: F401
from app.models.notification import Notification  # noqa: F401