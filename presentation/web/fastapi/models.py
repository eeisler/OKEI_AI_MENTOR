from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    first_name: str = Field(...)
    last_name: Optional[str] = Field(...)
    middle_name: Optional[str] = Field(...)
    group_id: Optional[int] = Field(...)

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