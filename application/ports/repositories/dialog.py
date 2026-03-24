from abc import ABC, abstractmethod
from typing import List
from domain.entities.dialog import Dialog

class DialogRepository(ABC):
    @abstractmethod
    def save(self, dialog: Dialog) -> Dialog:
        pass

    @abstractmethod
    def get_recent_dialogs(self, user_id) -> List[Dialog] | None:
        pass
    
    @abstractmethod
    def find_by_id(self, dialog_id) -> Dialog | None:
        pass
