from abc import ABC, abstractmethod
from entities.user import User

import psycopg2
from config import Config

config = Config.load()


class UserRepository(ABC):
    @abstractmethod
    def save(self, user) -> User:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> User | None:
        pass

    @abstractmethod
    def delete(self, id: int):
        pass




