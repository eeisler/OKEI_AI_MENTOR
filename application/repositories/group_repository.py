# application/repositories/group_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.study import Groups

class GroupRepository(ABC):
    @abstractmethod
    async def save(self, group: Groups) -> Groups:
        """Save or update a group"""
        pass

    @abstractmethod
    async def find_by_id(self, group_id: int) -> Optional[Groups]:
        """Find group by ID"""
        pass

    @abstractmethod
    async def find_by_specialty(self, specialty_id: int) -> List[Groups]:
        """Find all groups for a specialty"""
        pass

    @abstractmethod
    async def find_active_groups(self) -> List[Groups]:
        """Find all active groups"""
        pass

    @abstractmethod
    async def find_by_year(self, year: int) -> List[Groups]:
        """Find all groups for a specific course"""
        pass

    @abstractmethod
    async def delete(self, group_id: int) -> bool:
        """Delete a group"""
        pass