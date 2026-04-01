from application.repositories.dialog import DialogRepository
from domain.entities.dialog import Dialog
import logging
import datetime

logger = logging.getLogger(__name__)

class DialogService:
    def __init__(self, repository:DialogRepository):
        self.repository=repository
    
    async def save_dialog(
        self,
        user_id: int,
        user_messege: str,
        ai_responce: str,
        user_messege_time: datetime,
        ai_responce_time: datetime
    ) -> Dialog:
        dialog = Dialog(
            user_id=user_id,
            user_messege=user_messege,
            ai_responce=ai_responce,
            user_messege_time=user_messege_time,
            ai_responce_time=ai_responce_time
        )
        dialog = await self.repository.save(dialog)
        logger.info(f'Dialog {dialog.id} saved successfully')

        return dialog

    async def get_user_history(
        self, 
        user_id: int,
        limit: int = 10
    ):
        dialogs = self.repository.get_recent_dialogs(user_id=user_id, limit=limit)

        messages = []
        for message in dialogs:
            messages.extend(message.to_context_messages())
        
        return messages
