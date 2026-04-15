# application/repositories/specialization_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.study import Specialty

class SpecialtyRepository(ABC):
    @abstractmethod
    async def save(self, specialty: Specialty) -> Specialty:
        """Save or update a specialty"""
        pass

    @abstractmethod
    async def find_by_id(self, specialty_id: int) -> Optional[Specialty]:
        """Find specialty by ID"""
        pass

    @abstractmethod
    async def find_by_code(self, code: str) -> Optional[Specialty]:
        """Find specialty by code"""
        pass

    @abstractmethod
    async def find_by_department(self, department_id: int) -> List[Specialty]:
        """Find all specialties in a department"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Specialty]:
        """Find all specialties"""
        pass

    @abstractmethod
    async def delete(self, specialty_id: int) -> bool:
        """Delete a specialty"""
        pass