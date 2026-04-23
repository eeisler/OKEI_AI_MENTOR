import logging
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.student_progress_repository import StudentProgressRepository
from domain.entities.student_progress import StudentProgress
from infrastructure.database.models import StudentProgressModel
from exceptions import StudentProgressNotFound

logger = logging.getLogger(__name__)

class AsyncPostgresStudentProgressRepository(StudentProgressRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, student_progress: StudentProgress) -> StudentProgress:
        try:
            db_progress = StudentProgressModel(
                student_id=student_progress.student_id,
                skill_id=student_progress.skill_id,
                level=student_progress.level,
                weaknesses=student_progress.weaknesses
            )
            self.session.add(db_progress)
            await self.session.commit()
            await self.session.refresh(db_progress)
            student_progress.id = db_progress.id
            return student_progress
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't save student progress: {e}")
            raise

    async def find_by_student_id(self, student_id: int) -> List[StudentProgress]:
        result = await self.session.execute(
            select(StudentProgressModel).where(StudentProgressModel.student_id == student_id)
        )
        rows = result.scalars().all()
        return [
            StudentProgress(
                student_id=r.student_id,
                skill_id=r.skill_id,
                level=r.level,
                weaknesses=r.weaknesses,
                id=r.id
            ) for r in rows
        ]

    async def find_by_id(self, progress_id: int) -> Optional[StudentProgress]:
        result = await self.session.execute(
            select(StudentProgressModel).where(StudentProgressModel.id == progress_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise StudentProgressNotFound(progress_id=progress_id)
        
        return StudentProgress(
            student_id=row.student_id,
            skill_id=row.skill_id,
            level=row.level,
            weaknesses=row.weaknesses,
            id=row.id
        )

    async def find_by_student_and_skill(self, student_id: int, skill_id: int) -> Optional[StudentProgress]:
        result = await self.session.execute(
            select(StudentProgressModel).where(
                StudentProgressModel.student_id == student_id,
                StudentProgressModel.skill_id == skill_id
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
            
        return StudentProgress(
            student_id=row.student_id,
            skill_id=row.skill_id,
            level=row.level,
            weaknesses=row.weaknesses,
            id=row.id
        )
