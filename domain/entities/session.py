from dataclasses import dataclass
import datetime


@dataclass
class Session:
    id: int
    user_id: int
    is_ended: bool
    content: str
    created_at: datetime
    ended_at: datetime