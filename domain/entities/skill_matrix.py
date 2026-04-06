from dataclasses import dataclass
from domain.entities.study import Specialties


@dataclass
class SkillMatrix:
    id: int
    specialization: Specialties | None
    course: int | None
    skill: str | None
    description: str | None
    criterions: str | None

    def get_specialization(self):
        return self.specialization
    