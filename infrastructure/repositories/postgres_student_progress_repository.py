import logging
import psycopg2

from application.repositories.student_progress_repository import StudentProgressRepository
from domain.entities.student_progress import StudentProgress
from exceptions import StudentProgressNotFound
from infrastructure.database.connection import DataBaseConnection

logger = logging.getLogger(__name__)

class PostgresStudentProgressRepository(StudentProgressRepository):
    def __init__(self, db: DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    id SERIAL PRIMARY KEY,
                    student_id BIGINT REFERENCES users(user_id),
                    skill_id BIGINT REFERENCES skill_matrix(id),
                    level INT,
                    weaknesses TEXT
                )
            """)
            self.db.commit()
    
    def save(self, student_progress: StudentProgress):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO student_progress (student_id, skill_id, level, weaknesses)
                    VALUES (%s, %s, %s, %s)
                """, (student_progress.student_id, student_progress.skill_id, 
                      student_progress.level, student_progress.weaknesses))
            self.db.commit()  
        except psycopg2.Error as e:
            logger.error(f"Couldn't save student progress: {e}")
            self.db.rollback()
            raise  

    def find_by_student_id(self, student_id: int) -> list[StudentProgress]:
        """Find all progress records for a student"""
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, student_id, skill_id, level, weaknesses
                    FROM student_progress
                    WHERE student_id = %s
                """, (student_id,))  
                
                results = cur.fetchall()
                if not results:
                    return []
                
                progress_records = []
                for result in results:
                    progress = StudentProgress(
                        student_id=result['student_id'],
                        skill_id=result['skill_id'],
                        level=result['level'],
                        weaknesses=result['weaknesses']
                    )
                    progress.id = result['id']  
                    progress_records.append(progress)
                
                return progress_records
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find student progress by student_id {student_id}: {e}")
            raise

    def find_by_id(self, progress_id: int) -> StudentProgress | None:
        """Find a specific progress record by its ID"""
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, student_id, skill_id, level, weaknesses
                    FROM student_progress
                    WHERE id = %s
                """, (progress_id,))
                
                result = cur.fetchone()
                if not result:
                    raise StudentProgressNotFound(progress_id=progress_id)
                
                progress = StudentProgress(
                    student_id=result['student_id'],
                    skill_id=result['skill_id'],
                    level=result['level'],
                    weaknesses=result['weaknesses']
                )
                progress.id = result['id']
                return progress
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find progress by id {progress_id}: {e}")
            raise

    def find_by_student_and_skill(self, student_id: int, skill_id: int) -> StudentProgress | None:
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, student_id, skill_id, level, weaknesses
                    FROM student_progress
                    WHERE student_id = %s AND skill_id = %s
                """, (student_id, skill_id))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                progress = StudentProgress(
                    student_id=result['student_id'],
                    skill_id=result['skill_id'],
                    level=result['level'],
                    weaknesses=result['weaknesses']
                )
                progress.id = result['id']
                return progress
        except psycopg2.Error as e:
            logger.error(f"Couldn't find progress: {e}")
            return None