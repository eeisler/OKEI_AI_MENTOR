from abc import abstractmethod, ABC
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

    
