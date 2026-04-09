# application/repositories/specialization_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.study import Specialties

class SpecialityRepository(ABC):
    @abstractmethod
    def save(self, specialty: Specialties) -> Specialties:
        """Save or update a specialty"""
        pass

    @abstractmethod
    def find_by_id(self, specialty_id: int) -> Optional[Specialties]:
        """Find specialty by ID"""
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Specialties]:
        """Find specialty by code"""
        pass

    @abstractmethod
    def find_by_department(self, department_id: int) -> List[Specialties]:
        """Find all specialties in a department"""
        pass

    @abstractmethod
    def find_all(self) -> List[Specialties]:
        """Find all specialties"""
        pass

    @abstractmethod
    def delete(self, specialty_id: int) -> bool:
        """Delete a specialty"""
        pass