#main.py
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import Config

from infrastructure.database.connection import DataBaseConnection
from infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from infrastructure.repositories.postres_dialog_repository import PostgresDialogRepository
from infrastructure.ai.yandex_ai_service import YandexAIService

from presentation.tg.message import MessageHandler

config = Config.load()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def setup_repositories(db: DataBaseConnection):
    return {
        'user': PostgresUserRepository(db),
        'dialog': PostgresDialogRepository(db)
    }

def setup_services(repositories, config: Config):
    yandex_ai = YandexAIService(config)

    ai_context_service = AIContextService(
        dialog_repository=repositories['dialog'],
        ai_service=yandex_ai,
        instruction=config.ai_instruction
    )

    return {
        'user': UserService(repositories['user']),
        'dialog': DialogService(repositories['dialog']),
        'ai_context': ai_context_service
    }

def setup_handlers(servises, config: Config):
    message_handler = MessageHandler(
        user_service=services['user'],
        dialog_service=services['dialog'],
        ai_service=services['ai_context']
    )

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
    
    bot = Bot(token=config.bot_token,
    default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        ))
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

if __name__ == "__main__":
    asyncio.run(main())
