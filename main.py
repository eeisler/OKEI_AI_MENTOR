#main.py
import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import BasicAuth
from dotenv import load_dotenv

from application.repositories.session_repository import SessionRepository
from application.repositories.skill_matrix_repository import SkillMatrixRepository
from application.repositories.student_progress_repository import StudentProgressRepository
from config.config import Config
from datetime import datetime, timezone


from infrastructure.ai.yandex_ai_service import YandexAIService
from infrastructure.ai.qwen_ai_service import QwenAIService
from application.services.ai_service import AIContextService
from application.services.user_service import UserService
from application.services.dialog_service import DialogService

from domain.entities.session import Session
from domain.entities.skill_matrix import SkillMatrix
from domain.entities.student_progress import StudentProgress
from domain.entities.user import User, UserRole
from domain.entities.study import Specialty, Department, Groups
from domain.entities.dialog import Dialog

from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from typing import Optional, Any

from infrastructure.database.connection import get_db
from infrastructure.repositories.postgres_user_repository import AsyncPostgresUserRepository
from infrastructure.repositories.postgres_skill_matrix_repository import AsyncPostgresSkillMatrixRepository
from infrastructure.repositories.postgres_student_progress_repository import AsyncPostgresStudentProgressRepository
from infrastructure.repositories.postgres_group_repository import AsyncPostgresGroupRepository
from infrastructure.repositories.postgres_dialog_repository import AsyncPostgresDialogRepository
from infrastructure.repositories.postgres_specialty_repository import AsyncPostgresSpecialtyRepository
from application.services.user_service import UserService
from application.services.auth import hash_password, verify_password, create_access_token

from presentation.web.fastapi.models import *

load_dotenv()
config = Config.load()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9080"
    ],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

async def get_user_service(db: AsyncSession = Depends(get_db)):
    user_repo = AsyncPostgresUserRepository(db)
    skill_repo = AsyncPostgresSkillMatrixRepository(db)
    progress_repo = AsyncPostgresStudentProgressRepository(db)

    return UserService(user_repo, skill_repo, progress_repo)

async def get_group_repo(db: AsyncSession = Depends(get_db)):
    return AsyncPostgresGroupRepository(db)

async def get_dialog_service(db: AsyncSession = Depends(get_db)):
    return DialogService(AsyncPostgresDialogRepository(db))

async def get_ai_service(db: AsyncSession = Depends(get_db)):
    return AIContextService(
        dialog_service = DialogService(AsyncPostgresDialogRepository(db)),
        dialog_repository = AsyncPostgresDialogRepository(db),
        ai_service = QwenAIService(),
        matrix_repository = AsyncPostgresSkillMatrixRepository(db),
        student_progress_repository = AsyncPostgresStudentProgressRepository(db),
        user_repository = AsyncPostgresUserRepository(db),
        speciality_repository = AsyncPostgresSpecialtyRepository(db),
        instruction = config.ai_instruction
    )


@app.get("/groups")
async def get_groups(group_repo: AsyncPostgresGroupRepository = Depends(get_group_repo)):
    groups = await group_repo.find_active_groups()

    return [
        {"id": g.id, "name": f"{datetime.now.year - g.year}"}
        for g in groups
    ]

@app.post('/register')
async def register(
    data: RegisterRequest,
    service: UserService = Depends(get_user_service),
    group_repo: AsyncPostgresGroupRepository = Depends(get_group_repo)
):
    existing = await service.user_repo.find_by_username(data.username)

    if existing:
        return JSONResponse(
            status_code=400,
            content={'success': False, 'error': "Username already exists"}
        )
    
    group = None
    if data.group_id:
        group = await group_repo.find_by_id(int(data.group_id))

    hashed_password = hash_password(password)

    user = await service.get_or_create_user(
        username=username,
        hashed_password=hashed_password,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        group=group
    )
    return JSONResponse({
        "succsess": True,
        "user_id": user.id,
        "username": user.username
    })

@app.post('/login')
async def login_page(
    data: LoginRequest, 
    service: UserService = Depends(get_user_service)
    ):

    user = await service.user_repo.find_by_username(data.username)

    if not user or not verify_password(data.password, user.hashed_password):
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "Invalid credentials"}
        )

    token = create_access_token({"sub": user.username, "user_id": user.id})

    return JSONResponse({
        "success": True, 
        "token": token, 
        "user":{
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name
        }
    })

@app.post('/chat')
async def chat(
        data: ChatRequest,
        ai_service: AIContextService = Depends(get_ai_service),
        dialog_service: DialogService = Depends(get_dialog_service)
    ):
    user_id = 1
    user_message = data.message
    user_message_time = datetime.now()

    result = {}

    print("-"*100 + f"\n{data.message}")

    if data.message == '/task':
        ai_task = await ai_service.start_skill_session(user_id)
        result = {"message": ai_task}
    else:
        ai_response = await ai_service.get_response_with_history(user_id=user_id, user_message=user_message)
        ai_response_time = datetime.now()

        await dialog_service.save(
            user_id=user_id, 
            user_message=user_message, 
            ai_response=ai_response,
            question_id = None,
            user_message_time = user_message_time,
            ai_response_time = ai_response_time)

        result = {"message": ai_response}

    return result

@app.get("/chat/history")
async def show_chat(dialog_service: DialogService = Depends(get_dialog_service)):
    user_id = 1
    dialogs = await dialog_service.get_user_history(user_id=user_id, limit = 1000, question_id = None)
    messages = []
    for dialog in dialogs:
        if dialog.user_message:  
            messages.append({
                "id":  f"{dialog.id}user",
                "role": "user",
                "content": dialog.user_message,
                "timestamp": dialog.user_message_time
            })
        if dialog.ai_response:  
            messages.append({
                "id": f"{dialog.id}ai",
                "role": "ai",
                "content": dialog.ai_response,
                "timestamp": dialog.ai_response_time
            })
    
    return {
        "user_id": user_id,
        "messages": messages
    }
