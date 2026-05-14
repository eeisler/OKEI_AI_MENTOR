from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    group_id: Optional[int] = Field(None, description="Group ID if exists")

class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: dict

class LoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class LoginResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    user: dict

class ChatRequest(BaseModel):
    message: str = Field(...)

class MessageResponse(BaseModel):
    id: int
    role: str 
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    user_id: int