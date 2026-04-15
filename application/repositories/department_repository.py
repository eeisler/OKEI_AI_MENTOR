# application/repositories/department_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.study import Department

class DepartmentRepository(ABC):
    @abstractmethod
    async def save(self, department: Department) -> Department:
        """Save or update a department"""
        pass

    @abstractmethod
    async def find_by_id(self, department_id: int) -> Optional[Department]:
        """Find department by ID"""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Department]:
        """Find department by name"""
        pass

    @abstractmethod
    async def find_all(self) -> List[Department]:
        """Find all departments"""
        pass

    @abstractmethod
    async def delete(self, department_id: int) -> bool:
        """Delete a department"""
        pass