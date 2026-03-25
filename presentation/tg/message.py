# presentation/tg/message.py
import logging
import datetime
from aiogram import Router
from aiogram.types import Message

from application.services.user_service import UserService
from application.services.dialog_service import DialogService
from application.services.ai_service import AIContextService
from domain.entities.user import UserRole
from domain.entities.dialog import Dialog

logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(
        self, 
        user_service: UserService,
        dialog_service: DialogService,
        ai_service: AIContextService
    ):
        self.user_service = user_service
        self.dialog_service = dialog_service
        self.ai_service = ai_service
        self.router = Router()
        self._register_handlers()
    
    def _register_handlers(self):
        @self.router.message()  
        async def handle_message(message: Message):
            await self._handle_message(message) 
            
    async def _handle_message(self, message: Message):  
        if not message.text:
            await message.answer("Пока я могу работать только с текстовыми запросами")
            return

        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action='typing'
        ) 

        user_message_time = datetime.datetime.now() 

        user_id = message.from_user.id
        user_text = message.text
        
        logger.info(f'User message: {user_text}')

        try:
            user = await self.user_service.get_or_create_user(
                user_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                middle_name=None,
                role=UserRole.STUDENT
            )
        except Exception as e:
            logger.error(f"Couldn't access user {user_id}: {e}")
            await message.answer("Ошибка доступа к пользователю. Попробуйте позже.")
            return

        ai_response = None
        ai_response_time = None

        try:
            ai_response = await self.ai_service.get_response_with_history(
                user_id=user_id, 
                user_message=user_text
            )
            await message.answer(ai_response)
            ai_response_time = datetime.datetime.now()  
        except Exception as e:
            logger.error(f'AI response error for user {user_id}: {e}')
            await message.answer(f'Извините, произошла ошибка. Попробуйте позже.')
            return

        if ai_response:
            dialog = Dialog(
                user_id=user_id,
                user_message=user_text,          
                ai_response=ai_response,          
                user_message_time=user_message_time,
                ai_response_time=ai_response_time
            )

            try:
                await self.dialog_service.save_dialog(dialog)
                logger.info(f"Dialog saved for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to save dialog for user {user_id}: {e}")