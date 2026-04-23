import logging
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.dialog_repository import DialogRepository
from domain.entities.dialog import Dialog
from infrastructure.database.models import DialogModel  # Твоя модель из models.py
from domain.exceptions.errors import DataBaseError # Подправь импорт под свой проект

logger = logging.getLogger(__name__)

class AsyncPostgresDialogRepository(DialogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, dialog: Dialog) -> Dialog:
        try:
            db_dialog = DialogModel(
                user_id=dialog.user_id,
                user_message=dialog.user_message,
                ai_response=dialog.ai_response,
                question_id=dialog.question_id,
                user_message_time=dialog.user_message_time,
                ai_response_time=dialog.ai_response_time
            )
            
            self.session.add(db_dialog)
            await self.session.commit()
            await self.session.refresh(db_dialog)
            
            dialog.id = db_dialog.id
            logger.info(f"Dialog {dialog.id} saved for user {dialog.user_id}")
            return dialog
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"DB Error for user {dialog.user_id}: {e}")
            raise DataBaseError(str(e), user_id=dialog.user_id, operation='save_dialog')

    async def get_recent_dialogs(
        self, 
        user_id: int, 
        limit: int = 10,
        question_id: int = None
    ) -> List[Dialog]:
        try:
            query = select(DialogModel).where(DialogModel.user_id == user_id)
            
            if question_id:
                query = query.where(DialogModel.question_id == question_id)
            
            query = query.order_by(desc(DialogModel.user_message_time)).limit(limit)
            
            result = await self.session.execute(query)
            rows = result.scalars().all()
            
            return [
                Dialog(
                    id=row.id,
                    user_id=row.user_id,
                    user_message=row.user_message,
                    ai_response=row.ai_response,
                    question_id=row.question_id,
                    user_message_time=row.user_message_time,
                    ai_response_time=row.ai_response_time
                ) for row in rows
            ]
                
        except Exception as e:
            logger.error(f"DB error: Couldn't find dialogs for user {user_id}: {e}")
            raise DataBaseError(str(e), user_id=user_id, operation='get_recent_dialogs')

    async def find_by_id(self, dialog_id: int) -> Optional[Dialog]:
        try:
            result = await self.session.execute(
                select(DialogModel).where(DialogModel.id == dialog_id)
            )
            row = result.scalar_one_or_none()
            
            if not row:
                return None
            
            return Dialog(
                id=row.id,
                user_id=row.user_id,
                user_message=row.user_message,
                ai_response=row.ai_response,
                question_id=row.question_id,
                user_message_time=row.user_message_time,
                ai_response_time=row.ai_response_time
            )
        except Exception as e:
            logger.error(f"DB error: Couldn't find dialog by id {dialog_id}: {e}")
            raise DataBaseError(str(e), operation='find_dialog_by_id')
