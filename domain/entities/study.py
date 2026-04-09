from dataclasses import dataclass
from enum import Enum


@dataclass
class Department:
    id: int
    name: str


@dataclass
class Specialty:
    id: int
    code: str
    short_name: str
    full_name: str
    department: Department


@dataclass
class Groups:
    id: int
    course: int
    specialty: Specialty
    group_number: int
    is_active: bool

    def get_specialty(self):
        return self.specialty
    
    def get_course(self):
        return self.course