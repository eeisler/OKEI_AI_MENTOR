from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.dialog import Dialog


class DialogRepository(ABC):
    @abstractmethod
    async def save(self, dialog: Dialog) -> Dialog:
        pass

    @abstractmethod
    async def get_recent_dialogs(
        self, 
        user_id: int, 
        limit: int = 10,
        question_id: int = None
    ) -> List[Dialog]:
        pass
    
    @abstractmethod
    async def get_dialogs_by_question(
        self,
        user_id: int,
        question_id: int
    ) -> List[Dialog]:
        pass
    
    @abstractmethod
    async def find_by_id(self, dialog_id: int) -> Optional[Dialog]:
        pass