# infrastructure/repositories/postgres_specialty_repository.py
import psycopg2
from psycopg2 import extras
from typing import List, Optional
from application.repositories.specialty_repository import SpecialtyRepository
from domain.entities.study import Specialty, Department
from infrastructure.database.connection import DataBaseConnection
import logging

logger = logging.getLogger(__name__)

class PostgresSpecialtyRepository(SpecialtyRepository):
    def __init__(self, db: DataBaseConnection):
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS specialties (
                    id SERIAL PRIMARY KEY,
                    code TEXT NOT NULL UNIQUE,
                    short_name TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE
                )
            """)
            self.db.commit()
            logger.info("Specialty table created/verified")

    async def save(self, specialty: Specialty) -> Specialty:
        try:
            with self.db.get_cursor() as cur:
                if specialty.id:
                    # Update existing
                    cur.execute("""
                        UPDATE specialties 
                        SET code = %s, short_name = %s, full_name = %s, department_id = %s
                        WHERE id = %s
                        RETURNING id, code, short_name, full_name, department_id
                    """, (specialty.code, specialty.short_name, specialty.full_name, 
                          specialty.department.id, specialty.id))
                else:
                    # Insert new
                    cur.execute("""
                        INSERT INTO specialties (code, short_name, full_name, department_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, code, short_name, full_name, department_id
                    """, (specialty.code, specialty.short_name, specialty.full_name, 
                          specialty.department.id))
                
                result = cur.fetchone()
                if result:
                    specialty.id = result[0]
                    specialty.code = result[1]
                    specialty.short_name = result[2]
                    specialty.full_name = result[3]
                    # Department is already set in the entity
                
                self.db.commit()
                logger.info(f"Specialty {specialty.id} saved successfully")
                return specialty
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't save specialty: {e}")
            raise

    async def find_by_id(self, specialty_id: int) -> Optional[Specialty]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT s.id, s.code, s.short_name, s.full_name, s.department_id,
                           d.id as dept_id, d.name as dept_name
                    FROM specialties s
                    JOIN departments d ON s.department_id = d.id
                    WHERE s.id = %s
                """, (specialty_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                department = Department(
                    id=result['dept_id'],
                    name=result['dept_name']
                )
                
                return Specialty(
                    id=result['id'],
                    code=result['code'],
                    short_name=result['short_name'],
                    full_name=result['full_name'],
                    department=department
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find specialty by id {specialty_id}: {e}")
            return None

    async def find_by_code(self, code: str) -> Optional[Specialty]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT s.id, s.code, s.short_name, s.full_name, s.department_id,
                           d.id as dept_id, d.name as dept_name
                    FROM specialties s
                    JOIN departments d ON s.department_id = d.id
                    WHERE s.code = %s
                """, (code,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                department = Department(
                    id=result['dept_id'],
                    name=result['dept_name']
                )
                
                return Specialty(
                    id=result['id'],
                    code=result['code'],
                    short_name=result['short_name'],
                    full_name=result['full_name'],
                    department=department
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find specialty by code {code}: {e}")
            return None

    async def find_by_department(self, department_id: int) -> List[Specialty]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT s.id, s.code, s.short_name, s.full_name, s.department_id,
                           d.id as dept_id, d.name as dept_name
                    FROM specialties s
                    JOIN departments d ON s.department_id = d.id
                    WHERE s.department_id = %s
                    ORDER BY s.code
                """, (department_id,))
                
                results = cur.fetchall()
                specialties = []
                for result in results:
                    department = Department(
                        id=result['dept_id'],
                        name=result['dept_name']
                    )
                    specialties.append(Specialty(
                        id=result['id'],
                        code=result['code'],
                        short_name=result['short_name'],
                        full_name=result['full_name'],
                        department=department
                    ))
                return specialties
        except psycopg2.Error as e:
            logger.error(f"Couldn't find specialties for department {department_id}: {e}")
            return []

    async def find_all(self) -> List[Specialty]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT s.id, s.code, s.short_name, s.full_name, s.department_id,
                           d.id as dept_id, d.name as dept_name
                    FROM specialties s
                    JOIN departments d ON s.department_id = d.id
                    ORDER BY s.code
                """)
                
                results = cur.fetchall()
                specialties = []
                for result in results:
                    department = Department(
                        id=result['dept_id'],
                        name=result['dept_name']
                    )
                    specialties.append(Specialty(
                        id=result['id'],
                        code=result['code'],
                        short_name=result['short_name'],
                        full_name=result['full_name'],
                        department=department
                    ))
                return specialties
        except psycopg2.Error as e:
            logger.error(f"Couldn't find specialties: {e}")
            return []

    async def delete(self, specialty_id: int) -> bool:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("DELETE FROM specialties WHERE id = %s", (specialty_id,))
                self.db.commit()
                deleted = cur.rowcount > 0
                if deleted:
                    logger.info(f"Specialty {specialty_id} deleted")
                return deleted
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't delete specialty {specialty_id}: {e}")
            raise