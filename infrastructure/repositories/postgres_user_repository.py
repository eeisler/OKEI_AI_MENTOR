import logging
import psycopg2
from psycopg2 import extras

from application.repositories.user_repository import UserRepository
from domain.entities.user import User
from infrastructure.database.connection import DataBaseConnection

logger = logging.getLogger(__name__)

class PostgresUserRepository(UserRepository):
    def __init__(self, db: DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:  
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        course INTEGER,
                        registered_at TIMESTAMP DEFAULT NOW()
                    )
                """)
            self.db.commit()  

    async def save(self, user: User):
        try:
            with self.db.get_cursor() as cur: 
                cur.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name, course)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        course = EXCLUDED.course
                """, (user.user_id, user.username, user.first_name, user.last_name, user.course))
                self.db.commit() 
        except psycopg2.Error as e:
            self.db.rollback()  
            logger.error(f"Couldn't save user {user.user_id}: {e}")
            raise

    def find_by_id(self, user_id: int) -> User | None:
        try:
            with self.db.get_cursor(cursor_factory=extras.DictCursor) as cur: 
                cur.execute("""
                    SELECT user_id, username, first_name, last_name, course, registered_at
                    FROM users
                    WHERE user_id = %s
                """, (user_id,))
                result = cur.fetchone()
                if not result:
                    return None
                
                return User(
                    user_id=result['user_id'],
                    username=result['username'],
                    first_name=result['first_name'],
                    last_name=result['last_name'],
                    course=result['course'],
                    registered_at=result['registered_at']
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find user by id {user_id}: {e}")
            return None

    def delete(self, user_id: int):
        try:
            with self.db.get_cursor() as cur: 
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                self.db.commit()  
        except psycopg2.Error as e:
            self.db.rollback()  
            logger.error(f"Couldn't delete user {user_id}: {e}")
            raise
    
    def update_last_active(self, user_id: int) -> None:
        pass
