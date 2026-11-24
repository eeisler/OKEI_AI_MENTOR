from abc import ABC, abstractmethod
from domain.entities.user import User


class UserRepository(ABC):
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Создает нового пользователя в БД (INSERT)."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновляет существующего пользователя в БД (UPDATE)."""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        """Удаляет пользователя из БД по ID."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        """Находит пользователя по ID."""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """Находит пользователя по имени пользователя (логину)."""
        pass

    @abstractmethod
    async def find_users_with_active_streak(self) -> list[User]:
        """Возвращает всех пользователей с current_streak > 0."""
        pass

    @abstractmethod
    async def find_active_students(self) -> list[User]:
        """возвращает студентов из активных групп"""
        pass