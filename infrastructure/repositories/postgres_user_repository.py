import logging
import psycopg2
from psycopg2.extras import DictCursor
from domain.exceptions.errors import UserNotFound
from application.repositories.user_repository import UserRepository
from infrastructure.database.connection import DataBaseConnection
from domain.entities.user import User, UserRole

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
                    user_id SERIAL PRIMARY KEY,
                    first_name TEXT,
                    middle_name TEXT,
                    last_name TEXT,
                    role TEXT DEFAULT 'student',
                    group_id BIGINT
                )
            """)
            self.db.commit()

    async def save(self, user: User):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO users (first_name, middle_name, last_name, role, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING user_id
                """, (
                    user.first_name,
                    user.middle_name,
                    user.last_name,
                    user.role.value if user.role else "student",
                    user.group.id if user.group else None
                ))
                user_id = cur.fetchone()[0]
                self.db.commit()
                user.id = user_id
                return user
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Failed to save user: {e}")
            raise

    async def find_by_id(self, user_id: int) -> User | None:
        try:
            with self.db.get_cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT user_id, first_name, middle_name, last_name, role, group_id
                    FROM users
                    WHERE user_id = %s
                """, (user_id,))
                result = cur.fetchone()
                
                if not result:
                    raise UserNotFound(user_id=user_id)
                
                role = UserRole(result['role']) if result['role'] else UserRole.STUDENT
                
                return User(
                    id=result['user_id'],
                    first_name=result['first_name'],
                    middle_name=result['middle_name'],
                    last_name=result['last_name'],
                    role=role,
                    group=None
                )
                
        except UserNotFound:
            raise
        except psycopg2.Error as e:
            logger.error(f"Couldn't find user by id {user_id}: {e}")
            raise UserNotFound(user_id=user_id)

    async def find_by_id_with_group(self, user_id: int, group_repository) -> User | None:
        user = await self.find_by_id(user_id)
        if user and user.group:
            group = await group_repository.find_by_id(user.group.id)
            user.group = group
        return user

    async def update_last_active(self, user_id: int) -> None:
        pass

    async def delete(self, user_id: int) -> None:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    DELETE FROM users WHERE user_id = %s
                """, (user_id,))
                self.db.commit()
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise