from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any


@dataclass
class Department:
    id: Optional[int] = None
    name: str = None


@dataclass
class Specialty:
    id: Optional[int] = None
    code: str = None
    short_name: str = None
    full_name: str = None
    department: Any = None


@dataclass
class Groups:
    id: Optional[int] = None
    year: int = None
    specialty: Any = None
    group_number: int = None
    is_active: bool = False
    

    def get_specialty(self):
        return self.specialty
    
    def get_course(self):
        return self.course