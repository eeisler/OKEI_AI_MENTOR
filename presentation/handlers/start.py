#start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command


router = Router()

@router.message(Command('start'))
async def say_hello(message: Message):
    await message.answer(f"Hi, I'm OKEI AI-mentor bot")