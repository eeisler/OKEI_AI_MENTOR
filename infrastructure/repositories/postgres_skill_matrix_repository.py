import logging
from typing import List, Optional
import psycopg2
from psycopg2 import extras

from application.repositories.skill_matrix_repository import SkillMatrixRepository
from domain.entities.skill_matrix import SkillMatrix
from exceptions import SkillNotFound
from infrastructure.database.connection import DataBaseConnection

logger = logging.getLogger(__name__)

class PostgesSkillMatrixRepository(SkillMatrixRepository):
    def __init__(self, db: DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_table()

    def create_table(self):
        try:
            with self.db.get_cursor() as cur:
                # Проверяем существование таблицы specialties
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'specialties'
                    )
                """)
                specialties_exists = cur.fetchone()[0]
                
                if not specialties_exists:
                    # Создаем таблицу specialties если её нет
                    cur.execute("""
                        CREATE TABLE specialties (
                            id SERIAL PRIMARY KEY,
                            code TEXT NOT NULL UNIQUE,
                            short_name TEXT NOT NULL,
                            full_name TEXT NOT NULL,
                            department_id INTEGER
                        )
                    """)
                    logger.info("Specialties table created")
                
                # Создаем skill_matrix с правильным внешним ключом
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS skill_matrix (
                        id SERIAL PRIMARY KEY,
                        specialization_id INTEGER NOT NULL,
                        skill TEXT NOT NULL,
                        course INTEGER,
                        description TEXT,
                        criterions TEXT,
                        FOREIGN KEY (specialization_id) REFERENCES specialties(id) ON DELETE CASCADE
                    )
                """)
                self.db.commit()
                logger.info("Skill matrix table created/verified")

        except psycopg2.Error as e:
            logger.error(f"Couldn't create skill matrix table: {e}")
            self.db.rollback()
            raise

    def save(self, skill: SkillMatrix):
        try:
            with self.db.get_cursor() as cur:
                # Проверяем существует ли Speciality
                cur.execute("SELECT id FROM specialties WHERE id = %s", (skill.specialization_id,))
                if not cur.fetchone():
                    raise ValueError(f"Speciality with id {skill.specialization_id} does not exist")
                
                cur.execute("""
                    INSERT INTO skill_matrix (specialization_id, skill, course, description, criterions)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (skill.specialization_id, skill.skill, skill.course, 
                      skill.description, skill.criterions))
                
                result = cur.fetchone()
                if result:
                    skill.id = result[0]
                
                self.db.commit()
                logger.info(f"Skill saved with id {skill.id}")
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't save skill into matrix: {e}")
            self.db.rollback()
            raise

    def find_by_id(self, skill_id: int) -> SkillMatrix:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, specialization_id, skill, course, description, criterions
                    FROM skill_matrix
                    WHERE id = %s
                """, (skill_id,))
                
                result = cur.fetchone()
                if not result:
                    raise SkillNotFound(f"Skill with id {skill_id} not found")
                
                skill = SkillMatrix(
                    specialization_id=result['specialization_id'], 
                    skill=result['skill'], 
                    course=result['course'],
                    description=result['description'],
                    criterions=result['criterions']
                )
                skill.id = result['id']
                return skill
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find skill by id {skill_id}: {e}")
            raise
    
    def find_by_course_and_specialty(self, course: int, specialty_id: int) -> List[SkillMatrix]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, specialization_id, skill, course, description, criterions
                    FROM skill_matrix
                    WHERE course = %s AND specialization_id = %s
                    ORDER BY id
                """, (course, specialty_id))
                
                results = cur.fetchall()
                skills = []
                for result in results:
                    skill = SkillMatrix(
                        specialization_id=result['specialization_id'],
                        skill=result['skill'],
                        course=result['course'],
                        description=result['description'],
                        criterions=result['criterions']
                    )
                    skill.id = result['id']
                    skills.append(skill)
                return skills
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find skills for course {course}, specialty {specialty_id}: {e}")
            return []

    def delete(self, skill_id: int) -> bool:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("DELETE FROM skill_matrix WHERE id = %s", (skill_id,))
                self.db.commit()
                deleted = cur.rowcount > 0
                if deleted:
                    logger.info(f"Skill {skill_id} deleted")
                return deleted
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't delete skill {skill_id}: {e}")
            raise

    def update(self, skill: SkillMatrix) -> SkillMatrix:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE skill_matrix 
                    SET specialization_id = %s, skill = %s, course = %s, 
                        description = %s, criterions = %s
                    WHERE id = %s
                    RETURNING id
                """, (skill.specialization_id, skill.skill, skill.course,
                      skill.description, skill.criterions, skill.id))
                
                self.db.commit()
                logger.info(f"Skill {skill.id} updated")
                return skill
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't update skill {skill.id}: {e}")
            raise