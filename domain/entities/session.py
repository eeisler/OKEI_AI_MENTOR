from dataclasses import dataclass


@dataclass
class Session:
    id: int
    user_id: int
    is_ended: bool
    content: str