from dataclasses import dataclass
from enum import Enum

@dataclass
class Groups:
    id: int
    course: int
    specialty: Specialties
    group_number: int
    is_active: bool

    def get_specialty(self):
        return self.specialty
    
    def get_course(self):
        return self.course

@dataclass
class Specialties:
    id: int
    code: str
    short_name: str
    full_name: str
    department: Department

@dataclass
class Department:
    id: int
    name: str

