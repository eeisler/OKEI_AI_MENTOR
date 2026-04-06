from application.repositories.student_progress_repository import StudentProgressRepository
from domain.entities.student_progress import StudentProgress


class PostgresStudentProgressRepository(StudentProgressRepository):
    def __init__(self, db: DataBaseConnection):
        super().__init__()
        self.db = db
        self.create_table()

    def create_table(self):
        with self.db.get_cursor() as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS student_progress (
                        id BIGINT PRIMARY KEY,
                        student_id  BIGINT REFERENCES users(user_id),
                        skill_id  BIGINT REFERENCES skill_matrix(id),
                        level INT,
                        weaknesses TEXT
                        )
                """)
            self.db.commit()
    
    def save(self, student_progress: StudentProgress):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                        INSERT INTO student_progress (student_id, skill_id, level, weakness)
                        VALUES (%s, %s, %s, %s)
                    """, (student_progress.student_id, student_progress.skill_id, student_progress.level, student_progress.weakness))
        except psycopg2.Error as e:
            self.db.rollback()

    def find_by_id(self, user_id: int) -> User | None:
        try:
            with self.db.get_cursor(cursor_factory=DictCursor) as cur:
                 cur.execute("""
                    SELECT skill_id, level, weakness
                    FROM student_progress
                    WHERE student_id = %s
                """, (user_id))
                result = cur.fetchone()
                if not result:
                    raise UserNotFound(user_id=user_id)
                return User(**result)
        except psycopg2.Error as e:
            logger.error("Couldn't find user by id")
            raise UserNotFound(user_id=user_id)