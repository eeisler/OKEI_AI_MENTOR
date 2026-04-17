from dataclasses import dataclass
from domain.entities.study import Specialty
from typing import Optional


@dataclas
class SkillMatrix:
    id: Optional[int] = None
    specialty_id: int = None
    course: int = None
    skill: str = None
    description: str = None
    criterions: str = None

    def get_specialization(self):
        return self.Specialty
    