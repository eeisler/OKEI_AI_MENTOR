import psycopg2
from config import config
import psycopg2.extras
from contextlib import contextmanager


class DataBaseService:
    def __init__(self):
        self.connection_params = {
            'host': config.DB_HOST,
            'port': config.DB_PORT,
            'database': config.DB_NAME,
            'user': config.DB_USER,
            'password': config.DB_PASSWORD
        }
        self.conn = psycopg2.connect(**self.connection_params)
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Таблица пользователей
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registered_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Таблица диалогов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dialogs (
                    dialog_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()
    def save_dialog(self, user_id, user_message, ai_response, user_info):
        try:
            with self.conn.cursor() as cur:
                if user_info:
                    cur.execute("""
                        INSERT INTO users (user_id, username)
                        VALUES (%s, %s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id, user_info.get('username')))
                else:
                    cur.execute("""
                        INSERT INTO users (user_id) VALUES (%s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id,))
                
                cur.execute("""
                    INSERT INTO dialogs (user_id, user_message, ai_response)
                    VALUES (%s, %s, %s)
                """, (user_id, user_message, ai_response))
                
                self.conn.commit()
                print(f"✅ Диалог для пользователя {user_id} сохранён")
                return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            self.conn.rollback()
            return False
        
    def get_recent_dialogs(self, user_id, limit=10):
        """Возвращает последние диалоги пользователя в формате для нейросети"""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT user_message, ai_response 
                    FROM dialogs 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (user_id, limit))
                
                rows = cur.fetchall()
                
                # Превращаем в список сообщений в хронологическом порядке (сначала старые)
                messages = []
                for row in reversed(rows):  # reversed чтобы шли от старых к новым
                    messages.append({
                        "role": "user",
                        "content": row['user_message']
                    })
                    messages.append({
                        "role": "assistant",
                        "content": row['ai_response']
                    })
                
                return messages
        except Exception as e:
            print(f"❌ Ошибка при получении истории: {e}")
            return []
        
    
    def close(self):
        """Закрываем соединение (вызвать при остановке бота)"""
        if self.conn:
            self.conn.close()
            print("🔌 Соединение с БД закрыто")


db_service = DataBaseService()
