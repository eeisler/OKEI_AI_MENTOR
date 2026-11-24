import logging
from datetime import date 
from sqlalchemy import select, update, delete 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload 

from domain.exceptions.errors import UserNotFound
from application.repositories.user_repository import UserRepository
from domain.entities.user import User, UserRole
from domain.entities.study import Groups, Specialty
from infrastructure.database.models import UserModel, GroupModel, SpecialtyModel 

logger = logging.getLogger(__name__)

class AsyncPostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_domain(self, db_user: UserModel) -> User:
        group = None
        if db_user.group is not None:
            specialty = None
            if hasattr(db_user.group, 'specialty') and db_user.group.specialty is not None:
                specialty = Specialty(
                    id=db_user.group.specialty.id,
                    code=db_user.group.specialty.code,
                    short_name=db_user.group.specialty.short_name,
                    full_name=db_user.group.specialty.full_name,
                )
            group = Groups(
                id=db_user.group.id,
                year=db_user.group.year,
                specialty=specialty,
                group_number=db_user.group.group_number,
                is_active=db_user.group.is_active,
            )

        return User(
            id=db_user.id,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
            first_name=db_user.first_name,
            middle_name=db_user.middle_name,
            last_name=db_user.last_name,
            role=UserRole(db_user.role),
            group=group,
            current_streak=db_user.current_streak,
            longest_streak=db_user.longest_streak,
            last_activity_date=db_user.last_activity_date,
        )
    
    async def find_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(UserModel)
            .options(
                joinedload(UserModel.group)
                .joinedload(GroupModel.specialty)
            )
            .where(UserModel.id == user_id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None
        
        return self._to_domain(db_user)

    async def find_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(UserModel)
            .options(
                joinedload(UserModel.group)
                .joinedload(GroupModel.specialty)
            )
            .where(UserModel.username == username)
        )
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
            
        return self._to_domain(db_user)

    async def save(self, user: User) -> User:
        """Создает НОВОГО пользователя в БД (INSERT)."""
        db_user = UserModel(
            id=user.id,
            username=user.username,        
            hashed_password=user.hashed_password, 
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            group_id=user.group.id if user.group else None,
            current_streak=user.current_streak,
            longest_streak=user.longest_streak,
            last_activity_date=user.last_activity_date,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user) 
        user.id = db_user.id
        
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
                    group_id=user.group.id if user.group else None,
                    current_streak=user.current_streak,
                    longest_streak=user.longest_streak,
                    last_activity_date=user.last_activity_date,
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"User {user.id} updated successfully")
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

    async def find_users_with_active_streak(self) -> list[User]:
        stmt = (
            select(UserModel)
            .options(
                joinedload(UserModel.group)
                .joinedload(GroupModel.specialty)
            )
            .where(UserModel.current_streak > 0)
        )
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        return [self._to_domain(u) for u in db_users]
    
    async def find_active_students(self) -> list[User]:
        stmt = (
            select(UserModel)
            .options(
                joinedload(UserModel.group)
                .joinedload(GroupModel.specialty)
            )
            .where(
                UserModel.role == UserRole.STUDENT.value,
                UserModel.group.has(GroupModel.is_active.is_(True)),
            )
        )
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        return [self._to_domain(u) for u in db_users]