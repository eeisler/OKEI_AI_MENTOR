# infrastructure/repositories/postgres_department_repository.py
import psycopg2
from psycopg2 import extras
from typing import List, Optional
from application.repositories.department_repository import DepartmentRepository
from domain.entities.study import Department
from infrastructure.database.connection import DataBaseConnection
import logging

logger = logging.getLogger(__name__)

class PostgresDepartmentRepository(DepartmentRepository):
    def __init__(self, db: DataBaseConnection):
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            self.db.commit()
            logger.info("Departments table created")

    async def save(self, department: Department) -> Department:
        try:
            with self.db.get_cursor() as cur:
                if department.id:
                    cur.execute("""
                        UPDATE departments 
                        SET name = %s
                        WHERE id = %s
                        RETURNING id, name
                    """, (department.name, department.id))
                else:
                    cur.execute("""
                        INSERT INTO departments (name)
                        VALUES (%s)
                        RETURNING id, name
                    """, (department.name))
                
                result = cur.fetchone()
                if result:
                    department.id = result[0]
                    department.name = result[1]
                
                self.db.commit()
                logger.info(f"Department {department.id} saved successfully")
                return department
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't save department: {e}")
            raise

    async def find_by_id(self, department_id: int) -> Optional[Department]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, name
                    FROM departments
                    WHERE id = %s
                """, (department_id))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                return Department(
                    id=result['id'],
                    name=result['name']
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find department by id {department_id}: {e}")
            return None

    async def find_by_name(self, name: str) -> Optional[Department]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, name
                    FROM departments
                    WHERE name = %s
                """, (name))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                return Department(
                    id=result['id'],
                    name=result['name']
                )
        except psycopg2.Error as e:
            logger.error(f"Couldn't find department by name {name}: {e}")
            return None

    async def find_all(self) -> List[Department]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, name
                    FROM departments
                    ORDER BY name
                """)
                
                results = cur.fetchall()
                departments = []
                for result in results:
                    departments.append(Department(
                        id=result['id'],
                        name=result['name']
                    ))
                return departments

        except psycopg2.Error as e:
            logger.error(f"Couldn't find departments: {e}")
            return []

    async def delete(self, department_id: int) -> bool:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM specialties WHERE department_id = %s
                """, (department_id,))
                
                count = cur.fetchone()[0]
                if count > 0:
                    logger.warning(f"Cannot delete department {department_id} - has {count} specialties")
                    return False
                
                cur.execute("DELETE FROM departments WHERE id = %s", (department_id,))
                self.db.commit()
                deleted = cur.rowcount > 0
                if deleted:
                    logger.info(f"Department {department_id} deleted")
                return deleted
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't delete department {department_id}: {e}")
            raise