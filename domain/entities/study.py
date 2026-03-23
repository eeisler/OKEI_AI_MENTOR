from dataclasses import dataclass
from enum import Enum

@dataclass
class Groups:
    id: int
    course: int
    specialties: Specialties
    group_number: int
    is_active: bool

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

