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
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS skill_matrix (
                        id SERIAL PRIMARY KEY,
                        specialty_id INTEGER NOT NULL REFERENCES specialties(id),
                        course INTEGER,
                        skill TEXT NOT NULL,
                        description TEXT,
                        criterions TEXT
                    )
                """)
                self.db.commit()
                logger.info("Skill matrix table created")

        except psycopg2.Error as e:
            logger.error(f"Couldn't create skill matrix table: {e}")
            self.db.rollback()
            raise

    async def save(self, skill: SkillMatrix):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO skill_matrix (specialty_id, course, skill, description, criterions)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, specialty_id, skill, course, description, criterions
                """, (skill.specialty_id, skill.course, skill.skill, 
                    skill.description, skill.criterions))
                
                result = cur.fetchone()

                if result:
                    skill.id = result[0]
                    skill.specialty_id = result[1]
                    skill.skill = result[2]
                    skill.description = result[3]
                    skill.criterions = result[4]
            
                self.db.commit()
                logger.info(f"Skill saved with id {skill.id}")
                return skill
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't save skill into matrix: {e}")
            self.db.rollback()
            raise

    async def find_by_id(self, skill_id: int) -> SkillMatrix:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, specialty_id, skill, course, description, criterions
                    FROM skill_matrix
                    WHERE id = %s
                """, (skill_id,))
                
                result = cur.fetchone()
                if not result:
                    raise SkillNotFound(f"Skill with id {skill_id} not found")
                
                skill = SkillMatrix(
                    specialty_id=result['specialty_id'], 
                    course=result['course'],
                    skill=result['skill'], 
                    description=result['description'],
                    criterions=result['criterions']
                )
                skill.id = result['id']
                return skill
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find skill by id {skill_id}: {e}")
            raise
    
    async def find_by_course_and_specialty(self, course: int, specialty_id: int) -> List[SkillMatrix]:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, specialty_id, course, skill, description, criterions
                    FROM skill_matrix
                    WHERE course = %s AND specialty_id = %s
                    ORDER BY id
                """, (course, specialty_id))
                
                results = cur.fetchall()
                skills = []
                for result in results:
                    skill = SkillMatrix(
                        specialty_id=result['specialty_id'],
                        course=result['course'],
                        skill=result['skill'],
                        description=result['description'],
                        criterions=result['criterions']
                    )
                    skill.id = result['id']
                    skills.append(skill)
                return skills
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find skills for course {course}, specialty {specialty_id}: {e}")
            return []

    async def delete(self, skill_id: int) -> bool:
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

    async def update(self, skill: SkillMatrix) -> SkillMatrix:
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE skill_matrix 
                    SET specialty_id = %s, course = %s, skill = %s,
                        description = %s, criterions = %s
                    WHERE id = %s
                    RETURNING id
                """, (skill.specialty_id, skill.course, skill.skill,
                      skill.description, skill.criterions, skill.id))
                
                self.db.commit()
                logger.info(f"Skill {skill.id} updated")
                return skill
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't update skill {skill.id}: {e}")
            raise