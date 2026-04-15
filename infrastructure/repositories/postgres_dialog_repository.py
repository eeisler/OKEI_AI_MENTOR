import asyncio
import logging
import psycopg2
from psycopg2 import extras
from typing import List, Optional

from application.repositories.dialog_repository import DialogRepository
from domain.entities.dialog import Dialog
from exceptions import DataBaseError, NoDataError
from infrastructure.database.connection import DataBaseConnection

logger = logging.getLogger(__name__)

class PostgresDialogRepository(DialogRepository):
    def __init__(self, db: DataBaseConnection):  
        self.db = db  
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:  
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dialogs (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    question_id INTEGER,
                    user_message_time TIMESTAMP DEFAULT NOW(),
                    ai_response_time TIMESTAMP DEFAULT NOW()
                )
            """)
            self.db.commit()
            logger.info("Dialogs table created/verified")

    async def save(self, dialog: Dialog) -> Dialog:
        if not all([dialog.user_id, dialog.user_message, dialog.ai_response]):
            empty_data = [d for d in [dialog.user_id, dialog.user_message, dialog.ai_response] if d is None]
            raise NoDataError(
                missing_fields=empty_data,
                user_id=dialog.user_id
            )
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO dialogs (user_id, user_message, ai_response, question_id, user_message_time, ai_response_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, user_message, ai_response, question_id, user_message_time, ai_response_time
                """, (dialog.user_id, dialog.user_message, dialog.ai_response, 
                      dialog.question_id, dialog.user_message_time, dialog.ai_response_time))
                
                result = cur.fetchone()
                self.db.commit()
                
                if result:
                    dialog.id = result[0]
                    dialog.user_id = result[1]
                    dialog.user_message = result[2]
                    dialog.ai_response = result[3]
                    dialog.question_id = result[4]
                    dialog.user_message_time = result[5]
                    dialog.ai_response_time = result[6]
                
                logger.info(f"Dialog {dialog.id} saved for user {dialog.user_id}")
                return dialog
                
        except psycopg2.Error as e:
            logger.error(f"DB Error for user {dialog.user_id}: {e}")
            self.db.rollback() 
            raise DataBaseError(
                str(e),
                user_id=dialog.user_id,
                operation='save_dialog'          
            )

    async def get_recent_dialogs(
        self, 
        user_id: int, 
        limit: int = 10,
        question_id: int = None
    ) -> List[Dialog]:
        try:
            with self.db.get_cursor(cursor_factory=extras.DictCursor) as cur:
                if question_id:
                    cur.execute("""
                        SELECT id, user_id, user_message, ai_response, question_id, 
                               user_message_time, ai_response_time
                        FROM dialogs
                        WHERE user_id = %s AND question_id = %s
                        ORDER BY user_message_time DESC
                        LIMIT %s
                    """, (user_id, question_id, limit))
                else:
                    cur.execute("""
                        SELECT id, user_id, user_message, ai_response, question_id, 
                               user_message_time, ai_response_time
                        FROM dialogs
                        WHERE user_id = %s
                        ORDER BY user_message_time DESC
                        LIMIT %s
                    """, (user_id, limit))

                rows = cur.fetchall()
                dialogs = []
                
                for row in rows:
                    dialog = Dialog(
                        id=row['id'],
                        user_id=row['user_id'],
                        user_message=row['user_message'],
                        ai_response=row['ai_response'],
                        question_id=row['question_id'],
                        user_message_time=row['user_message_time'],
                        ai_response_time=row['ai_response_time']
                    )
                    dialogs.append(dialog)
                
                return dialogs
                
        except psycopg2.Error as e:
            logger.error(f"DB error: Couldn't find dialogs for user {user_id}: {e}")
            raise DataBaseError(
                str(e),
                user_id=user_id,
                operation='get_recent_dialogs' 
            )

    async def get_dialogs_by_question(
        self,
        user_id: int,
        question_id: int
    ) -> List[Dialog]:
        try:
            with self.db.get_cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, user_id, user_message, ai_response, question_id, 
                           user_message_time, ai_response_time
                    FROM dialogs
                    WHERE user_id = %s AND question_id = %s
                    ORDER BY user_message_time ASC
                """, (user_id, question_id))
                
                rows = cur.fetchall()
                dialogs = []
                
                for row in rows:
                    dialog = Dialog(
                        id=row['id'],
                        user_id=row['user_id'],
                        user_message=row['user_message'],
                        ai_response=row['ai_response'],
                        question_id=row['question_id'],
                        user_message_time=row['user_message_time'],
                        ai_response_time=row['ai_response_time']
                    )
                    dialogs.append(dialog)
                
                return dialogs
                
        except psycopg2.Error as e:
            logger.error(f"DB error: Couldn't find dialogs for user {user_id}, question {question_id}: {e}")
            raise DataBaseError(
                str(e),
                user_id=user_id,
                operation='get_dialogs_by_question'
            )

    async def find_by_id(self, dialog_id: int) -> Optional[Dialog]:
        try:
            with self.db.get_cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, user_id, user_message, ai_response, question_id, 
                           user_message_time, ai_response_time
                    FROM dialogs
                    WHERE id = %s
                """, (dialog_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                return Dialog(
                    id=result['id'],
                    user_id=result['user_id'],
                    user_message=result['user_message'],
                    ai_response=result['ai_response'],
                    question_id=result['question_id'],
                    user_message_time=result['user_message_time'],
                    ai_response_time=result['ai_response_time']
                )
        except psycopg2.Error as e:
            logger.error(f"DB error: Couldn't find dialog by id {dialog_id}: {e}")
            raise DataBaseError(
                str(e),
                operation='find_dialog_by_id'
            )