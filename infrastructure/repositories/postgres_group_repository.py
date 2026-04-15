import psycopg2
from psycopg2 import extras
from typing import List, Optional
from application.repositories.group_repository import GroupRepository
from domain.entities.study import Groups, Specialty
from infrastructure.database.connection import DataBaseConnection
import logging

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
                    course INTEGER NOT NULL,
                    specialty_id INTEGER NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
                    group_number INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(specialty_id, group_number)
                )
            """)
            self.db.commit()
            logger.info("Groups table created/verified")

    async def save(self, group: Groups) -> Groups:
        try:
            with self.db.get_cursor() as cur:
                # Убедимся, что specialty сохранён и имеет ID
                if group.specialty and group.specialty.id is None:
                    raise ValueError("Specialty must be saved before group")
                
                specialty_id = group.specialty.id if group.specialty else None
                
                if group.id:
                    # Update existing
                    cur.execute("""
                        UPDATE groups 
                        SET course = %s, specialty_id = %s, group_number = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id, course, specialty_id, group_number, is_active, created_at, updated_at
                    """, (group.course, specialty_id, group.group_number, group.is_active, group.id))
                else:
                    # Insert new
                    cur.execute("""
                        INSERT INTO groups (course, specialty_id, group_number, is_active)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, course, specialty_id, group_number, is_active, created_at, updated_at
                    """, (group.course, specialty_id, group.group_number, group.is_active))
                
                result = cur.fetchone()
                if result:
                    group.id = result[0]
                    group.course = result[1]
                    # specialty_id is result[2] - need to load specialty if needed
                    group.group_number = result[3]
                    group.is_active = result[4]
                    # created_at = result[5], updated_at = result[6] - optional
                
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
                    SELECT g.id, g.course, g.specialty_id, g.group_number, g.is_active,
                           s.id as s_id, s.code as s_code, s.short_name as s_short_name, 
                           s.full_name as s_full_name, s.department_id as s_department_id
                    FROM groups g
                    JOIN specialties s ON g.specialty_id = s.id
                    WHERE g.id = %s
                """, (group_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                # Load specialty
                specialty = Specialty(
                    id=result['s_id'],
                    code=result['s_code'],
                    short_name=result['s_short_name'],
                    full_name=result['s_full_name'],
                    department_id=result['s_department_id']
                )
                
                return Groups(
                    id=result['id'],
                    course=result['course'],
                    specialty=specialty,
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
                    SELECT g.id, g.course, g.specialty_id, g.group_number, g.is_active,
                           s.id as s_id, s.code as s_code, s.short_name as s_short_name, 
                           s.full_name as s_full_name, s.department_id as s_department_id
                    FROM groups g
                    JOIN specialties s ON g.specialty_id = s.id
                    WHERE g.specialty_id = %s
                    ORDER BY g.group_number
                """, (specialty_id,))
                
                results = cur.fetchall()
                groups = []
                for result in results:
                    specialty = Specialty(
                        id=result['s_id'],
                        code=result['s_code'],
                        short_name=result['s_short_name'],
                        full_name=result['s_full_name'],
                        department_id=result['s_department_id']
                    )
                    groups.append(Groups(
                        id=result['id'],
                        course=result['course'],
                        specialty=specialty,
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
                    SELECT g.id, g.course, g.specialty_id, g.group_number, g.is_active,
                           s.id as s_id, s.code as s_code, s.short_name as s_short_name, 
                           s.full_name as s_full_name, s.department_id as s_department_id
                    FROM groups g
                    JOIN specialties s ON g.specialty_id = s.id
                    WHERE g.is_active = TRUE
                    ORDER BY g.course, g.group_number
                """)
                
                results = cur.fetchall()
                groups = []
                for result in results:
                    specialty = Specialty(
                        id=result['s_id'],
                        code=result['s_code'],
                        short_name=result['s_short_name'],
                        full_name=result['s_full_name'],
                        department_id=result['s_department_id']
                    )
                    groups.append(Groups(
                        id=result['id'],
                        course=result['course'],
                        specialty=specialty,
                        group_number=result['group_number'],
                        is_active=result['is_active']
                    ))
                return groups
        except psycopg2.Error as e:
            logger.error(f"Couldn't find active groups: {e}")
            return []

    async def find_by_course(self, course: int) -> List[Groups]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT g.id, g.course, g.specialty_id, g.group_number, g.is_active,
                           s.id as s_id, s.code as s_code, s.short_name as s_short_name, 
                           s.full_name as s_full_name, s.department_id as s_department_id
                    FROM groups g
                    JOIN specialties s ON g.specialty_id = s.id
                    WHERE g.course = %s
                    ORDER BY g.group_number
                """, (course,))
                
                results = cur.fetchall()
                groups = []
                for result in results:
                    specialty = Specialty(
                        id=result['s_id'],
                        code=result['s_code'],
                        short_name=result['s_short_name'],
                        full_name=result['s_full_name'],
                        department_id=result['s_department_id']
                    )
                    groups.append(Groups(
                        id=result['id'],
                        course=result['course'],
                        specialty=specialty,
                        group_number=result['group_number'],
                        is_active=result['is_active']
                    ))
                return groups
        except psycopg2.Error as e:
            logger.error(f"Couldn't find groups by course {course}: {e}")
            return []

    async def delete(self, group_id: int) -> bool:
        try:
            with self.db.get_cursor() as cur:
                # Check if group has any users before deleting
                cur.execute("SELECT COUNT(*) FROM users WHERE group_id = %s", (group_id,))
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