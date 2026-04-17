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
                    id SERIAL PRIMARY KEY,
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
                    RETURNING id
                """, (
                    user.first_name,
                    user.middle_name,
                    user.last_name,
                    user.role.value if user.role else "student",
                    user.group_id if user.group else None
                ))

                if result:
                    user.id = result[0]
                    user.first_name = result[1]
                    user.middle_name = result[2]
                    user.last_name = result[3]
                    user.role = result[4]
                    user.group_id = result[5]

                self.db.commit()
                logger.info("User saved with id {user.id}")
                return user
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Failed to save user: {e}")
            raise

    async def find_by_id(self, user_id: int) -> User | None:
        try:
            with self.db.get_cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT id, first_name, middle_name, last_name, role, group_id
                    FROM users
                    WHERE id = %s
                """, (user_id))
                result = cur.fetchone()
                
                role = UserRole(result['role']) if result['role'] else UserRole.STUDENT
                group = result['group'] if result['group'] else None
                
                return User(
                    id=result['user_id'],
                    first_name=result['first_name'],
                    middle_name=result['middle_name'],
                    last_name=result['last_name'],
                    role=role,
                    group=group
                )
                
        except UserNotFound:
            raise
        except psycopg2.Error as e:
            logger.error(f"Couldn't find user by id {user_id}: {e}")
            raise UserNotFound(user_id=user_id)

    async def update(self, user: User) -> User:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE users
                    SET first_name = %s, middle_name = %s, last_name = %s, role = %s, group_id = %s
                    WHERE id = %s
                    RETURNING id, first_name, middle_name, last_name, role, group_id
                """, (user.first_name, user.middle_name, user.last_name, user.role, user.group_id, user.id))
                
                self.db.commit()
                logger.info(f"User {user.id} updated")
                return user
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't update skill {skill.id}: {e}")
            raise

    async def delete(self, user_id: int) -> None:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    DELETE FROM users WHERE id = %s
                """, (user_id))
                self.db.commit()
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise