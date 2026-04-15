from application.repositories.dialog_repository import DialogRepository
from domain.entities.dialog import Dialog
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DialogService:
    def __init__(self, repository: DialogRepository):
        self.repository = repository
    
    async def save(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        question_id: int = None,
        user_message_time: datetime = None,
        ai_response_time: datetime = None
    ) -> Dialog:
        dialog = Dialog(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            question_id=question_id,
            user_message_time=user_message_time or datetime.now(),
            ai_response_time=ai_response_time or datetime.now()
        )
        dialog = await self.repository.save(dialog)
        logger.info(f'Dialog {dialog.id} saved successfully')
        return dialog

    async def get_user_history(
        self, 
        user_id: int,
        limit: int = 10,
        question_id: int = None
    ) -> list:
        """Get user conversation history, optionally filtered by question"""
        dialogs = await self.repository.get_recent_dialogs(
            user_id=user_id, 
            limit=limit,
            question_id=question_id
        )
        
        messages = []
        for dialog in dialogs:
            messages.extend(dialog.to_context_messages())
        
        return messages
