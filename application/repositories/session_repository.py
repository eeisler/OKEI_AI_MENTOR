from abc import abstractmethod, ABC
from domain.entities.session import Session

class SessionRepository(ABC):
    @abstractmethod
    def save(self, session: Session) -> Session:
        pass

    @abstractmethod
    def find_by_id(self, session_id: int) -> Session:
        pass

    @abstractmethod
    def create_session(self, session: Session) -> Session:
        pass

    @abstractmethod
    def end_session(self, session: Session) -> Session:
        pass
        