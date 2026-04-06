import logging
from typing import List

import psycopg2

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
                        specialization BIGINT REFERENCES specialization(id),
                        skill TEXT,
                        course INT,
                        description TEXT,
                        criterions TEXT    
                    )
                """)
                self.db.commit()

        except psycopg2.Error as e:
            logger.error(f"Couldn't create skill matrix table: {e}")
            self.db.rollback()
            raise  

    def save(self, skill: SkillMatrix):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO skill_matrix (specialization, skill, course, description, criterions)
                    VALUES (%s, %s, %s, %s, %s)
                """, (skill.specialization, skill.skill, skill.course, skill.description, skill.criterions))
            self.db.commit()  
        except psycopg2.Error as e:
            logger.error(f"Couldn't save skill into matrix: {e}")
            self.db.rollback()
            raise  

    def delete(self, skill: SkillMatrix):
        pass

    def find_by_id(self, skill_id: int) -> SkillMatrix:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, specialization, skill, course, description, criterions
                    FROM skill_matrix
                    WHERE id = %s
                """, (skill_id))
                
                result = cur.fetchone()
                if not result:
                    raise SkillNotFound(id=skill_id)
                
                skill = SkillMatrix(
                    student_id=result['id'],
                    specialization=result['specialization'], 
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
                    SELECT id, skill, criterions, specialization_id, course
                    FROM skill_matrix
                    WHERE course = %s AND specialization_id = %s
                    ORDER BY id
                """, (course, specialty_id))
                
                results = cur.fetchall()
                skills = []
                for result in results:
                    skills.append(SkillMatrix(
                        id=result['id'],
                        skill=result['skill'],
                        criterions=result['criterions'],
                        specialization_id=result['specialization_id'],
                        course=result['course']
                    ))
                return skills
        except psycopg2.Error as e:
            logger.error(f"Couldn't find skills for course {course}, specialty {specialty_id}: {e}")
            return []