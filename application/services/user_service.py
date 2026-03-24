from application.repositories.user import UserRepository
from domain.entities.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository
    
    async def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        user = await self.repository.find_by_id(user_id)

        if user is None:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role=role
            )
            user = self.repository.save(user)
            logger.info(f'User {user_id=} {username=} {role=} succfully created')
        else:
            logger.info('User was already created')

        return user

    

