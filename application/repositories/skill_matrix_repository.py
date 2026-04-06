from abc import abstractmethod, ABC
from typing import List
from domain.entities.skill_matrix import SkillMatrix


class SkillMatrixRepository(ABC):
    @abstractmethod
    def find_by_id(self, skill_id: int) -> SkillMatrix:
        pass

    @abstractmethod
    def save(self, skill: SkillMatrix) -> SkillMatrix:
        pass

    @abstractmethod
    def delete(self, skill: SkillMatrix):
        pass
    
    @abstractmethod
    def find_by_course_and_specialty(self, course: int, specialty_id: int) -> List[SkillMatrix]:
        pass
    
