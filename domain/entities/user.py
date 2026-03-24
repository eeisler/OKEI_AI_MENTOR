from dataclasses import dataclass, field
from enum import Enum



@dataclass
class UserRole(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

@dataclass
class User:
    id: int
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    role: UserRole = field(default_factory=lambda: UserRole.STUDENT)
    #group: Groups | None



