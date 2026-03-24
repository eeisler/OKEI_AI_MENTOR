#infrastracture/repositories/postgres_user_repository.py
import logging
import psycopg2

logger = logging.getLogger(__name__)


class PostgresUserRepository(UserRepository):
    def __init__(self, db: DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_tables()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        middle_name TEXT,
                        last_name TEXT
                    )
                """)
            self.db.commit()

    def save(self, user: User):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                        INSERT INTO users (user_id, username, first_name, middle_name, last_name)
                        VALUES (%s, %s, %s, %s)
                    """, (user.user_id, user.username, user.first_name, user.middle_name, user.last_name))
        except psycopg2.Error as e:
            self.db.rollback()

    def find_by_id(self, user_id: int) -> User | None:
        try:
            with self.db.get_cursor(cursor_factory=DictCursor) as cur:
                 cur.execute("""
                    SELECT username, first_name, middle_name, last_name
                    FROM users
                    WHERE user_id = %s
                    ORDER BY timastamp DESC
                """, (id))
        except psycopg2.Error as e:
            logger.error("Couldn't find user by id")
            raise UserNotFound(user_id=user_id)
    
    def update_last_active(self, user_id: int) -> None:
        pass

    def delete(self, user_id: int) -> None:
        pass
