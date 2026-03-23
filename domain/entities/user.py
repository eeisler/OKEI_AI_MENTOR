from dataclasses import dataclass
from enum import Enum
from . import entities


@dataclass
class UserType(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

@dataclass
class User:
    id: int
    name: str | None
    user_type: UserType = UserType.STUDENT
    group: Groups | None



