#help.py
from aiogram import Router
from aiogram.filters import Command


router = Router()
@router.message(Command('help'))
async def show_commands(message: Message):
    await message.answer('Help commands in progress')