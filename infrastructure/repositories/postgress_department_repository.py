import logging
from typing import List, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from application.repositories.department_repository import DepartmentRepository
from domain.entities.study import Department
from infrastructure.database.models import DepartmentModel, SpecialtyModel

logger = logging.getLogger(__name__)

class AsyncPostgresDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, department: Department) -> Department:
        try:
            if department.id:
                stmt = (
                    update(DepartmentModel)
                    .where(DepartmentModel.id == department.id)
                    .values(name=department.name)
                )
                await self.session.execute(stmt)
            else:
                db_dept = DepartmentModel(name=department.name)
                self.session.add(db_dept)
                await self.session.flush()
                department.id = db_dept.id

            await self.session.commit()
            logger.info(f"Department {department.id} saved successfully")
            return department
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't save department: {e}")
            raise

    async def find_by_id(self, department_id: int) -> Optional[Department]:
        result = await self.session.execute(
            select(DepartmentModel).where(DepartmentModel.id == department_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return Department(id=row.id, name=row.name)

    async def find_by_name(self, name: str) -> Optional[Department]:
        result = await self.session.execute(
            select(DepartmentModel).where(DepartmentModel.name == name)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return Department(id=row.id, name=row.name)

    async def find_all(self) -> List[Department]:
        result = await self.session.execute(
            select(DepartmentModel).order_by(DepartmentModel.name)
        )
        return [Department(id=r.id, name=r.name) for r in result.scalars().all()]

    async def delete(self, department_id: int) -> bool:
        try:
           count_res = await self.session.execute(
                select(func.count())
                .select_from(SpecialtyModel)
                .where(SpecialtyModel.department_id == department_id)
            )
            count = count_res.scalar()
            
            if count > 0:
                logger.warning(f"Cannot delete department {department_id} - has {count} specialties")
                return False

            res = await self.session.execute(
                delete(DepartmentModel).where(DepartmentModel.id == department_id)
            )
            await self.session.commit()
            return res.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't delete department {department_id}: {e}")
            raise
