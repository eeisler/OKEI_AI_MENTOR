#start.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()

@router.message(Command('start'))
async def say_hello(message: Message):
    await message.answer(f"Hi, I'm OKEI AI-mentor bot")