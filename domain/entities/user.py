from dataclasses import dataclass
from enum import Enum


@dataclass
class UserType(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

@dataclass
class User:
    id: int
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    user_type: UserType = UserType.STUDENT
    group: Groups | None



