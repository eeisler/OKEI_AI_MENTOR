import psycopg2
from psycopg2 import extras
from typing import List, Optional
from application.repositories.group_repository import GroupRepository
from domain.entities.study import Groups, Specialty
from infrastructure.database.connection import DataBaseConnection
import logging
from exceptions import DataBaseError

logger = logging.getLogger(__name__)

class PostgresGroupRepository(GroupRepository):
    def __init__(self, db: DataBaseConnection):
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id SERIAL PRIMARY KEY,
                    year INTEGER NOT NULL,
                    specialty_id INTEGER NOT NULL REFERENCES specialties(id),
                    group_number INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                    UNIQUE(year, specialty_id, group_number)
                )
            """)
            self.db.commit()
            logger.info("Groups table created")

    async def save(self, group: Groups) -> Groups:
        try:
            with self.db.get_cursor() as cur:                
                if group.id:
                    cur.execute("""
                        UPDATE groups 
                        SET year = %s, specialty_id = %s, group_number = %s, is_active = %s
                        WHERE id = %s
                        RETURNING id, year, specialty_id, group_number, is_active
                    """, (group.year, group.specialty_id, group.group_number, group.is_active, group.id))
                else:
                    cur.execute("""
                        INSERT INTO groups (year, specialty_id, group_number, is_active)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, year, specialty_id, group_number, is_active
                    """, (group.year, group.specialty_id, group.group_number, group.is_active))

                result = cur.fetchone()

                if not result:
                    logger.error("Couldn't save group")
                    raise DataBaseError()

                group.id = result[0]
                group.year = result[1]
                group.specialty_id = result[2]
                group.group_number = result[3]
                group.is_active = result[4]
                
                self.db.commit()
                logger.info(f"Group {group.id} saved successfully")
                return group
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't save group: {e}")
            raise

    async def find_by_id(self, group_id: int) -> Optional[Groups]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT g.id, g.year, g.specialty_id, g.group_number, g.is_active
                    FROM groups AS g
                    WHERE g.id = %s
                """, (group_id))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                return Groups(
                    id=result['id'],
                    year=result['year'],
                    specialty_id=result['specialty_id'],
                    group_number=result['group_number'],
                    is_active=result['is_active']
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find group by id {group_id}: {e}")
            return None

    async def find_by_specialty(self, specialty_id: int) -> List[Groups]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT g.id, g.year, g.specialty_id, g.group_number, g.is_active
                    FROM groups g
                    WHERE g.specialty_id = %s
                    ORDER BY g.year DESC
                """, (specialty_id))
                
                results = cur.fetchall()
                groups = []

                for result in results:
                    groups.append(Groups(
                        id=result['id'],
                        year=result['year'],
                        specialty_id=result['specialty_id'],
                        group_number=result['group_number'],
                        is_active=result['is_active']
                    ))
                return groups
        except psycopg2.Error as e:
            logger.error(f"Couldn't find groups by specialty {specialty_id}: {e}")
            return []

    async def find_active_groups(self) -> List[Groups]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT g.id, g.year, g.specialty_id, g.group_number, g.is_active
                    FROM groups g
                    WHERE g.is_active = TRUE
                    ORDER BY g.year DESC
                """)
                
                results = cur.fetchall()
                groups = []
                for result in results:
                    groups.append(Groups(
                        id=result['id'],
                        year=result['year'],
                        specialty_id=result['specialty_id'],
                        group_number=result['group_number'],
                        is_active=result['is_active']
                    ))
                return groups
        except psycopg2.Error as e:
            logger.error(f"Couldn't find active groups: {e}")
            return []

    async def find_by_year(self, year: int) -> List[Groups]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT g.id, g.year, g.specialty_id, g.group_number, g.is_active
                    FROM groups g
                    WHERE g.year = %s
                    ORDER BY g.year DESC
                """, (year))
                
                results = cur.fetchall()
                groups = []
                for result in results:
                    groups.append(Groups(
                        id=result['id'],
                        year=result['year'],
                        specialty_id=result['specialty_id'],
                        group_number=result['group_number'],
                        is_active=result['is_active']
                    ))
                return groups
        except psycopg2.Error as e:
            logger.error(f"Couldn't find groups by year {year}: {e}")
            return []

    async def delete(self, group_id: int) -> bool:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users WHERE group_id = %s", (group_id))
                count = cur.fetchone()[0]
                if count > 0:
                    logger.warning(f"Cannot delete group {group_id} - has {count} users")
                    return False
                
                cur.execute("DELETE FROM groups WHERE id = %s", (group_id,))
                self.db.commit()
                deleted = cur.rowcount > 0
                if deleted:
                    logger.info(f"Group {group_id} deleted")
                return deleted
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't delete group {group_id}: {e}")
            raise