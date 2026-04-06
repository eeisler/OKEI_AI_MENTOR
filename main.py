#main.py
import logging
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

from infrastructure.database.connection import DataBaseConnection
from infrastructure.repositories.postgres_student_progress_repository import PostgresStudentProgressRepository
from infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from infrastructure.repositories.postgres_dialog_repository import PostgresDialogRepository
from infrastructure.repositories.postgres_skill_matrix_repository import PostgesSkillMatrixRepository
from infrastructure.repositories.postgres_session_repository import PostgresSessionRepository

from infrastructure.ai.yandex_ai_service import YandexAIService
from application.services.ai_service import AIContextService
from application.services.user_service import UserService
from application.services.dialog_service import DialogService

from presentation.tg.start import router as start_router   
from presentation.tg.help import router as help_router 

from presentation.tg.message import MessageHandler

load_dotenv()
config = Config.load()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def setup_repositories(db: DataBaseConnection):
    return {
        'user': PostgresUserRepository(db),
        'dialog': PostgresDialogRepository(db),
        'skill_matrix': PostgesSkillMatrixRepository(db),
        'student_progress': PostgresStudentProgressRepository(db),
        'session': PostgresSessionRepository(db)
    }

def setup_services(repositories, config: Config):
    yandex_ai = YandexAIService(config)

    ai_context_service = AIContextService(
        dialog_service=DialogService(repositories['dialog']),
        ai_service=yandex_ai,
        instruction=config.ai_instruction
    )

    return {
        'user': UserService(repositories['user']),
        'dialog': DialogService(repositories['dialog']),
        'ai_context': ai_context_service
    }

def setup_handlers(services, config: Config):
    message_handler = MessageHandler(
        user_service=services['user'],
        dialog_service=services['dialog'],
        ai_service=services['ai_context']
    )
    
    return {
        'message': message_handler,
        'start': start_router,
        'help': help_router
    }


def register_routers(dp: Dispatcher, handlers):
    dp.include_router(handlers['message'].router)
    dp.include_router(handlers['start'])
    dp.include_router(handlers['help'])


async def main():
    config = Config.load()
    logger.info("Configuration loaded")
    
    db = DataBaseConnection(config)
    db.connect()
    logger.info("Database connected")
    
    repositories = setup_repositories(db)
    logger.info("Repositories created")
    
    services = setup_services(repositories, config)
    logger.info("Services created")
    
    handlers = setup_handlers(services, config)
    logger.info("Handlers created")
    
    

    #auth = BasicAuth(login=config.proxy_user, password=config.proxy_password)
    
    #session = AiohttpSession(config.proxy_url, auth)
      
"""
    bot = Bot(token=config.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        ),
        )
    
    dp = Dispatcher()
    
    register_routers(dp, handlers)
    logger.info("Routers registered")
    
    logger.info("Starting bot...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        db.close()
        logger.info("Resources cleaned up")
"""
if __name__ == "__main__":
    asyncio.run(main())
