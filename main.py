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


from infrastructure.ai.yandex_ai_service import YandexAIService
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

from typing import Optional, Any

from infrastructure.database.connection import get_db
from infrastructure.repositories.postgres_user_repository import AsyncPostgresUserRepository
from infrastructure.repositories.postgres_skill_matrix_repository import AsyncPostgresSkillMatrixRepository
from infrastructure.repositories.postgres_student_progress_repository import AsyncPostgresStudentProgressRepository
from infrastructure.repositories.postgres_group_repository import AsyncPostgresGroupRepository
from application.services.user_service import UserService
from application.services.auth import hash_password, verify_password, create_access_token

load_dotenv()
config = Config.load()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
templates = Jinja2Templates(directory='presentation/web/fastapi/templates')

async def get_user_service(db: AsyncSession = Depends(get_db)):
    user_repo = AsyncPostgresUserRepository(db)
    skill_repo = AsyncPostgresSkillMatrixRepository(db)
    progress_repo = AsyncPostgresStudentProgressRepository(db)

    return UserService(user_repo, skill_repo, progress_repo)

async def get_group_repo(db: AsyncSession = Depends(get_db)):
    return AsyncPostgresGroupRepository(db)
    
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="main.html", 
    context={})

@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    group_repo: AsyncPostgresGroupRepository = Depends(get_group_repo)
):
    groups_list = await group_repo.find_active_groups() 

    return templates.TemplateResponse(
    request=request, 
    name="register.html", 
    context={"groups": groups_list})

@app.post('/register')
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    last_name: str = Form(None),
    group_id: str = Form(None),
    service: UserService = Depends(get_user_service),
    group_repo: AsyncPostgresGroupRepository = Depends(get_group_repo)
):
    hashed_password = hash_password(password)
    print("-"*100)
    print(f"{group_id} type {type(int(group_id))}")

    group = await group_repo.find_by_id(int(group_id)) 

    print(group)

    await service.get_or_create_user(
        username=username,
        hashed_password=hashed_password,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        group=group
    )
    return RedirectResponse(url="/login", status_code=303)

@app.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="login.html", 
    context={})