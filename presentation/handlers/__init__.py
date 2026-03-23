from aiogram import Router
from . import start, help, message


router = Router()
router.include_router(start.router)
router.include_router(help.router)
router.include_router(message.router)