from abc import ABC, abstractmethod
from domain.entities.user import User
from domain.entities.student_progress import StudentProgress


class StudentProgressRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def save(self, student_progress: StudentProgress):
        pass