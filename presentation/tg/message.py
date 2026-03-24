    import aiogram 
    from aiogram.types import Message
    from aiogram import Router
    from application.services.user_service import UserService
    from application.services.dialog_service import DialogService
    from application.services.ai_service import AIContextService
    from domain.exception.errors import UserNotFound
    from domain.entitites.user import UserRole
    import datetime

    import logging

    logger = logging.getLogger(__name__) 
    router = Router()

    class MessageHandler:
        def __init__(
            self, 
            user_service: UserService,
            dialog_service: DialogService,
            ai_service: AIContextService
        )

        self.user_service = user_service
        self.dialog_service = dialog_service
        self.ai_service = ai_service
        self.router = Router()
        self._register_handlers()
        
        def _register_handlers(self):
            @self.router.message()  
            async def handle_message(message: Message):
                await self._handle_message(message)
                
        async def _handle_messages(self, message: Message):
            if not message.text:
                await message.answer("Пока я могу работать только с текстовыми запросами")

            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action='typing'
            ) 

            user_messege_time = datetime.now()

            user_id = message.from_user.id
            user_text = message.text
            
            logger.info(f'User message {user_text}')

            try:
                user = await self.user_service.get_or_create_user(
                    user_id=user_id,
                    username=message.from_user.username,
                    first_name = None,
                    last_name = None,
                    middle_name = None,
                    role=UserRole.STUDENT # TODO: add choosing the role for the bot
                )
            except Exception as e:
                logger.error("Couldn't access user")
                await message.answer("Ошибка доступа к пользователю. Попробуйте позже.")
                return

            ai_response = None
            ai_response_time = None

            try:
                ai_response = self.ai_service.get_response_with_history(user_id, user_text)
                await message.answer(f'{ai_response}')
                ai_responce_time = datetime.now()
            except Exception as e:
                logger.error('Ai responce error')
                await message.answer(f'{e}')

            if ai_responce:
                dialog = Dialog(
                    user_id=user_id,
                    user_messege=user_text,
                    ai_responce=ai_response,
                    user_messege_time=user_messege_time,
                    ai_responce_time=ai_responce_time
                )

                try:
                    await self.dialog_service.save_dialog(dialog)
                    logger.info(f"Dialog saved for user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to save dialog for user {user_id}: {e}")