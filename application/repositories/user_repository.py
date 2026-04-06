from abc import ABC, abstractmethod
from domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def update_last_active(self, user_id: int) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass
    