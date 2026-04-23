import logging
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.skill_matrix_repository import SkillMatrixRepository
from domain.entities.skill_matrix import SkillMatrix
from infrastructure.database.models import SkillMatrixModel
from exceptions import SkillNotFound

logger = logging.getLogger(__name__)

class AsyncPostgresSkillMatrixRepository(SkillMatrixRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, skill: SkillMatrix) -> SkillMatrix:
        try:
            db_skill = SkillMatrixModel(
                specialty_id=skill.specialty_id,
                course=skill.course,
                skill=skill.skill,
                description=skill.description,
                criterions=skill.criterions
            )
            self.session.add(db_skill)
            await self.session.commit()
            await self.session.refresh(db_skill)
            skill.id = db_skill.id
            logger.info(f"Skill saved with id {skill.id}")
            return skill
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't save skill into matrix: {e}")
            raise

    async def find_by_id(self, skill_id: int) -> SkillMatrix:
        result = await self.session.execute(
            select(SkillMatrixModel).where(SkillMatrixModel.id == skill_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise SkillNotFound(f"Skill with id {skill_id} not found")
        
        skill_entity = SkillMatrix(
            specialty_id=row.specialty_id,
            course=row.course,
            skill=row.skill,
            description=row.description,
            criterions=row.criterions
        )
        skill_entity.id = row.id
        return skill_entity

    async def find_by_course_and_specialty(self, course: int, specialty_id: int) -> List[SkillMatrix]:
        result = await self.session.execute(
            select(SkillMatrixModel)
            .where(
                SkillMatrixModel.course == course,
                SkillMatrixModel.specialty_id == specialty_id
            )
            .order_by(SkillMatrixModel.id)
        )
        
        skills = []
        for row in result.scalars().all():
            skill_entity = SkillMatrix(
                specialty_id=row.specialty_id,
                course=row.course,
                skill=row.skill,
                description=row.description,
                criterions=row.criterions
            )
            skill_entity.id = row.id
            skills.append(skill_entity)
        return skills

    async def delete(self, skill_id: int) -> bool:
        try:
            result = await self.session.execute(
                delete(SkillMatrixModel).where(SkillMatrixModel.id == skill_id)
            )
            await self.session.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Skill {skill_id} deleted")
            return deleted
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't delete skill {skill_id}: {e}")
            raise

    async def update(self, skill: SkillMatrix) -> SkillMatrix:
        try:
            stmt = (
                update(SkillMatrixModel)
                .where(SkillMatrixModel.id == skill.id)
                .values(
                    specialty_id=skill.specialty_id,
                    course=skill.course,
                    skill=skill.skill,
                    description=skill.description,
                    criterions=skill.criterions
                )
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Skill {skill.id} updated")
            return skill
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't update skill {skill.id}: {e}")
            raise
