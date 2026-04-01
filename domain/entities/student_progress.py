from dataclasses import dataclass
from domain.entities.skill_matrix import SkillMatrix

@dataclass
class StudentProgress:
    id: int
    student_id: int 
    skill_id: SkillMatrix 
    level: int
    weaknesses: str

    def get_weaknesses(self):
        return self.weaknesses

    