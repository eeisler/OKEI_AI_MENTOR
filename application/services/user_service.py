from application.repositories.skill_matrix_repository import SkillMatrixRepository
from application.repositories.student_progress_repository import StudentProgressRepository
from application.repositories.user_repository import UserRepository
from domain.entities.student_progress import StudentProgress
from domain.entities.user import User, UserRole
import logging


logger = logging.getLogger(__name__)

class UserService:
    def __init__(
            self,
            user_repository: UserRepository,
            skill_matrix_repository: SkillMatrixRepository,
            student_progress_repository: StudentProgressRepository
            ):
        self.repository = user_repository
        self.skill_matrix_repository = skill_matrix_repository
        self.student_progress_repository = student_progress_repository
    
    async def get_or_create_user(
        self,
        user_id: int | None = None,
        username: str | None = None,
        hashed_password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        user = await self.repository.find_by_id(user_id)

        if user is None:
            user = User(
                id=user_id,
                username=username,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                role=role
            )
            user = await self.repository.save(user)

            if user.role == UserRole.STUDENT:
                await self.initialize_student_progress(user)
            logger.info(f'User {user_id=} {username=} {role=} succfully created')
        else:
            logger.info('User was already created')

        return user

    async def initialize_student_progress(self, user: User):
        """Business logic: determine which skills to initialize"""
        group = user.group
        
        skills = await self.skill_matrix_repository.find_by_course_and_specialty(
            course= int(datetime.now.year) - group.year,
            specialty_id=group.specialty.id
        )
        
        for skill in skills:
            existing = await self.student_progress_repository.find_by_student_and_skill(
                user.id, skill.id
            )
            
            if not existing:
                progress = StudentProgress(
                    student_id=user.id,
                    skill_id=skill.id,
                    level=0,
                    weaknesses=""
                )
  
                await self.student_progress_repository.save(progress)

