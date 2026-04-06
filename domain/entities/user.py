from dataclasses import dataclass, field
from enum import Enum
from domain.entities.study import Groups


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
    group: Groups | None = None

    def get_group(self):
        return self.group

    def get_course(self): #define using start year
        return self.group.get_course()

    def get_specialty(self):
        return self.group.get_specialty()



