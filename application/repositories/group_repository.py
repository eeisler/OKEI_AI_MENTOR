# application/repositories/group_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.study import Groups

class GroupRepository(ABC):
    @abstractmethod
    def save(self, group: Groups) -> Groups:
        """Save or update a group"""
        pass

    @abstractmethod
    def find_by_id(self, group_id: int) -> Optional[Groups]:
        """Find group by ID"""
        pass

    @abstractmethod
    def find_by_specialty(self, specialty_id: int) -> List[Groups]:
        """Find all groups for a specialty"""
        pass

    @abstractmethod
    def find_active_groups(self) -> List[Groups]:
        """Find all active groups"""
        pass

    @abstractmethod
    def find_by_course(self, course: int) -> List[Groups]:
        """Find all groups for a specific course"""
        pass

    @abstractmethod
    def delete(self, group_id: int) -> bool:
        """Delete a group"""
        pass