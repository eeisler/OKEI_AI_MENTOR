from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Dialog:
    id: Optional[int] = None
    user_id: Optional[int] = None
    user_message: str = ""
    ai_response: str = ""
    question_id: Optional[int] = None
    user_message_time: Optional[datetime] = None
    ai_response_time: Optional[datetime] = None

    def __post_init__(self):
        if self.user_message_time is None:
            self.user_message_time = datetime.now()
        if self.ai_response_time is None:
            self.ai_response_time = datetime.now()

    def to_context_messages(self) -> list:
        return [
            {"role": "user", "content": self.user_message},
            {"role": "assistant", "content": self.ai_response}
        ]


@dataclass
class Question:
    id: Optional[int] = None
    question_text: str = ""
    skill_id: Optional[int] = None
    level: int 