import logging
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.specialty_repository import SpecialtyRepository
from domain.entities.study import Specialty
from infrastructure.database.models import SpecialtyModel

logger = logging.getLogger(__name__)

class AsyncPostgresSpecialtyRepository(SpecialtyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, specialty: Specialty) -> Specialty:
        try:
            if specialty.id:
                stmt = (
                    update(SpecialtyModel)
                    .where(SpecialtyModel.id == specialty.id)
                    .values(
                        code=specialty.code,
                        short_name=specialty.short_name,
                        full_name=specialty.full_name,
                        department_id=specialty.department_id
                    )
                )
                await self.session.execute(stmt)
            else:
                db_specialty = SpecialtyModel(
                    code=specialty.code,
                    short_name=specialty.short_name,
                    full_name=specialty.full_name,
                    department_id=specialty.department_id
                )
                self.session.add(db_specialty)
                await self.session.flush()
                specialty.id = db_specialty.id

            await self.session.commit()
            logger.info(f"Specialty {specialty.id} saved successfully")
            return specialty
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't save specialty: {e}")
            raise

    async def find_by_id(self, specialty_id: int) -> Optional[Specialty]:
        result = await self.session.execute(
            select(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return Specialty(
            id=row.id,
            code=row.code,
            short_name=row.short_name,
            full_name=row.full_name,
            department=row.department_id
        )

    async def find_by_department(self, department_id: int) -> List[Specialty]:
        result = await self.session.execute(
            select(SpecialtyModel)
            .where(SpecialtyModel.department_id == department_id)
            .order_by(SpecialtyModel.code)
        )
        return [
            Specialty(
                id=r.id, code=r.code, short_name=r.short_name,
                full_name=r.full_name, department_id=r.department_id
            ) for r in result.scalars().all()
        ]

    async def find_all(self) -> List[Specialty]:
        result = await self.session.execute(
            select(SpecialtyModel).order_by(SpecialtyModel.code)
        )
        return [
            Specialty(
                id=r.id, code=r.code, short_name=r.short_name,
                full_name=r.full_name, department_id=r.department_id
            ) for r in result.scalars().all()
        ]

    async def delete(self, specialty_id: int) -> bool:
        try:
            result = await self.session.execute(
                delete(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
            )
            await self.session.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Specialty {specialty_id} deleted")
            return deleted
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't delete specialty {specialty_id}: {e}")
            raise

    async def find_by_code():
        pass