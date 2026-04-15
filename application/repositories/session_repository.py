from abc import abstractmethod, ABC
from domain.entities.session import Session

class SessionRepository(ABC):
    @abstractmethod
    async def save(self, session: Session) -> Session:
        pass

    @abstractmethod
    async def find_by_id(self, session_id: int) -> Session:
        pass

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        pass

    @abstractmethod
    async def end_session(self, session: Session) -> Session:
        pass
        