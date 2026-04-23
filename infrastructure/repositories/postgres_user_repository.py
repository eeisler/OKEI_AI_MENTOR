import logging
from sqlalchemy import select, update, delete 
from sqlalchemy.ext.asyncio import AsyncSession
from domain.exceptions.errors import UserNotFound
from application.repositories.user_repository import UserRepository
from infrastructure.database.connection import DataBaseConnection
from domain.entities.user import User, UserRole
from infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)

class AsyncPostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None
        
        return User(
            id=db_user.id,
            username=db_user.username,       
            hashed_password=db_user.hashed_password, 
            first_name=db_user.first_name,
            middle_name=db_user.middle_name,
            last_name=db_user.last_name,
            role=UserRole(db_user.role)
        )

    async def find_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
            first_name=db_user.first_name,
            middle_name=db_user.middle_name,
            last_name=db_user.last_name,
            role=UserRole(db_user.role)
        )

    async def save(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            username=user.username,        
            hashed_password=user.hashed_password, 
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            group_id=user.group.id if user.group else None
        )
        self.session.add(db_user)
        await self.session.commit()
        return user

    async def update(self, user: User) -> User:
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    username=user.username,         
                    hashed_password=user.hashed_password, 
                    first_name=user.first_name,
                    middle_name=user.middle_name,
                    last_name=user.last_name,
                    role=user.role.value if hasattr(user.role, 'value') else user.role,
                    group_id=user.group.id if user.group else None
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"User {user.id} updated")
            return user
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't update user {user.id}: {e}")
            raise

    async def delete(self, user_id: int) -> None:
        try:
            stmt = delete(UserModel).where(UserModel.id == user_id)
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"User {user_id} deleted")
        except Exception as e:
            await self.session.rollback() 
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
