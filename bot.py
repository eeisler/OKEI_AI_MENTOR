#bot.py
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import Config
from handlers import router
from services.db_service import db_service 

config = Config.load()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )
)

dp = Dispatcher()
dp.include_router(router)

async def main():
    print('bot started')
    try:
        await dp.start_polling(bot)
    finally:
        db_service.close()
        print('Бот остановлен')

if __name__ == '__main__':
    asyncio.run(main())