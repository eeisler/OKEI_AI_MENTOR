from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    id: int 
    user_id: int = 0
    is_ended: bool = False
    content: str = ""
    created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None  