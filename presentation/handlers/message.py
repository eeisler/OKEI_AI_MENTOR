import aiogram 
from aiogram.types import Message
from aiogram import Router
from services.ai_service import ai_service
import logging
from services.db_service import db_service


logger = logging.getLogger(__name__) #
router = Router()

@router.message()
async def handle_messages(message: Message):
    if not message.text:
        await message.answer("Пока я могу работать только с текстовыми запросами")

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action='typing'
    ) 

    user_id = message.from_user.id
    user_text = message.text
    
    print(message.text)
    try:
        ai_response = ai_service.get_ai_response_with_context(user_id, user_text)
        await message.answer(f'{ai_response}')
    except Exception as e:
        #logger.error()
        await message.answer(f'{e}')

    db_service.save_dialog(
    user_id=user_id,
    user_message=user_text,
    ai_response=ai_response,
    user_info={
        'username': message.from_user.username
    }
    )