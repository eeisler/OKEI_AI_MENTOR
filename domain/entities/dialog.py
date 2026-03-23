from dataclasses import dataclass
from datetime import datetime


@dataclass
class Dialog:
    id: int
    user_id: int
    user_messege: str
    ai_responce: str
    user_messege_time: datetime
    ai_responce_time: datetime

# need to think about other parametrs cause we'll use MK
@dataclass
class Question:
    id: int
    question_text: str
    difficulty: str
