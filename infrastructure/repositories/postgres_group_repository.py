import logging
from typing import List, Optional
from sqlalchemy import select, update, delete, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from application.repositories.group_repository import GroupRepository
from domain.entities.study import Groups
from infrastructure.database.models import GroupModel, UserModel

logger = logging.getLogger(__name__)

class AsyncPostgresGroupRepository(GroupRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, group: Groups) -> Groups:
        try:
            if group.id:
                stmt = (
                    update(GroupModel)
                    .where(GroupModel.id == group.id)
                    .values(
                        year=group.year,
                        specialty_id=group.specialty_id,
                        group_number=group.group_number,
                        is_active=group.is_active
                    )
                )
                await self.session.execute(stmt)
            else:
                db_group = GroupModel(
                    year=group.year,
                    specialty_id=group.specialty_id,
                    group_number=group.group_number,
                    is_active=group.is_active
                )
                self.session.add(db_group)
                await self.session.flush()
                group.id = db_group.id

            await self.session.commit()
            logger.info(f"Group {group.id} saved successfully")
            return group
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't save group: {e}")
            raise

    async def find_by_id(self, group_id: int) -> Optional[Groups]:
        result = await self.session.execute(
            select(GroupModel).where(GroupModel.id == group_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return Groups(
            id=row.id,
            year=row.year,
            specialty_id=row.specialty_id,
            group_number=row.group_number,
            is_active=row.is_active
        )

    async def find_by_specialty(self, specialty_id: int) -> List[Groups]:
        result = await self.session.execute(
            select(GroupModel)
            .where(GroupModel.specialty_id == specialty_id)
            .order_by(desc(GroupModel.year))
        )
        return [
            Groups(
                id=r.id, year=r.year, specialty_id=r.specialty_id,
                group_number=r.group_number, is_active=r.is_active
            ) for r in result.scalars().all()
        ]

    async def find_active_groups(self) -> List[Groups]:
        result = await self.session.execute(
            select(GroupModel)
            .where(GroupModel.is_active == True)
            .order_by(desc(GroupModel.year))
        )
        return [
            Groups(
                id=r.id, year=r.year, specialty_id=r.specialty_id,
                group_number=r.group_number, is_active=r.is_active
            ) for r in result.scalars().all()
        ]

    async def find_by_year(self, year: int) -> List[Groups]:
        result = await self.session.execute(
            select(GroupModel)
            .where(GroupModel.year == year)
            .order_by(desc(GroupModel.year))
        )
        return [
            Groups(
                id=r.id, year=r.year, specialty_id=r.specialty_id,
                group_number=r.group_number, is_active=r.is_active
            ) for r in result.scalars().all()
        ]

    async def delete(self, group_id: int) -> bool:
        try:
            count_res = await self.session.execute(
                select(func.count()).select_from(UserModel).where(UserModel.group_id == group_id)
            )
            if count_res.scalar() > 0:
                return False
            
            res = await self.session.execute(
                delete(GroupModel).where(GroupModel.id == group_id)
            )
            await self.session.commit()
            return res.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Couldn't delete group {group_id}: {e}")
            raise
