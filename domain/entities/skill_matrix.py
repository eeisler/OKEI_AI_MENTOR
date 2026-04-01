from dataclasses import dataclass
from domain.entities.study import Specialties


@dataclass
class SkillMatrix:
    id: int
    specialization: Specialties | None
    course: int | None
    skill: str | None
    description: str | None
    criterion: str | None

    def get_specialty(self):
        return self.specialization
    