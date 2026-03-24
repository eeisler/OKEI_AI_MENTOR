from infrastructure.database.connection import DataBaseConnection
from application.repositories.dialog import DialogRepository
from domain.entities.dialog import Dialog


class PostgresDialogRepository(DialogRepository):
    def __init__(self, db : DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dialogs (
                    dialog_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    user_message_time TIMESTAMP DEFAULT NOW(),
                    ai_response_time TIMESTAMP DEFAULT NOW()
                )
            """)
            self.db.commit()

    def save(self, dialog: Dialog):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO dialogs (user_id, user_message, ai_response, user_message_time, ai_response_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (dialog.user_id, dialog.user_message, dialog.ai_response, dialog.user_message_time, dialog.ai_response_time))
        except psycopg2.Error as e:
            logging.error(f"DB Error for user {dialog.user_id}: {e}")
            self.db.rollback()
            raise DataBaseError(
                str(e),
                user_id=dialog.user_id,
                operation='save_dialog'          
                )
            

    def get_recent_dialogs(self, user_id, limit=10):
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT user_message, ai_response
                    FROM dialogs
                    WHERE user_id = %s
                    ORDER BY timastamp DESC
                    LIMIT %s
                """, (user_id, limit))

                rows = cur.fetchall()
                messages = []

                for row in reversed(rows):
                    messages.append({
                        "role":"user",
                        "content": row['user_message']
                    })
                    messages.append({
                        "role":"assistant",
                        "content": row["ai_response"]
                    })

                return messages
        except psycopg2.Error as e:
            logging.error(f"DB error: Couldn't find the dialogs for user {user_id}")
            raise DataBaseError(
                str(e),
                user_id=user_id,
                operation='find_dialog_by_user_id' 
            )
    
    def find_by_id(self, dialog_id:int) -> Dialog:
        pass        