# infrastructure/repositories/postgres_session_repository.py
import psycopg2
from psycopg2 import extras
from typing import Optional
from datetime import datetime

from application.repositories.session_repository import SessionRepository
from domain.entities.session import Session
from infrastructure.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class PostgresSessionRepository(SessionRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.create_table()

    def create_table(self):
        """Create sessions table if it doesn't exist"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    is_ended BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    ended_at TIMESTAMP
                )
            """)
            self.db.commit()
            logger.info("Sessions table created/verified")

    def save(self, session: Session) -> Session:
        """Save or update an existing session"""
        try:
            with self.db.get_cursor() as cur:
                # Check if session exists
                if session.id:
                    # Update existing session
                    cur.execute("""
                        UPDATE sessions 
                        SET user_id = %s, content = %s, is_ended = %s, ended_at = %s
                        WHERE id = %s
                        RETURNING id, user_id, content, is_ended, created_at, ended_at
                    """, (session.user_id, session.content, session.is_ended, 
                          session.ended_at, session.id))
                else:
                    # Insert new session
                    cur.execute("""
                        INSERT INTO sessions (user_id, content, is_ended, ended_at)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, user_id, content, is_ended, created_at, ended_at
                    """, (session.user_id, session.content, session.is_ended, 
                          session.ended_at))
                
                result = cur.fetchone()
                if result:
                    session.id = result[0]
                    session.user_id = result[1]
                    session.content = result[2]
                    session.is_ended = result[3]
                    session.created_at = result[4]
                    session.ended_at = result[5]
                
                self.db.commit()
                logger.info(f"Session {session.id} saved successfully")
                return session
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't save session: {e}")
            raise

    def find_by_id(self, session_id: int) -> Optional[Session]:
        """Find a session by its ID"""
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, user_id, content, is_ended, created_at, ended_at
                    FROM sessions
                    WHERE id = %s
                """, (session_id,))
                
                result = cur.fetchone()
                if not result:
                    logger.warning(f"Session {session_id} not found")
                    return None
                
                session = Session(
                    id=result['id'],
                    user_id=result['user_id'],
                    content=result['content'],
                    is_ended=result['is_ended'],
                    created_at=result['created_at'],
                    ended_at=result['ended_at']
                )
                
                return session
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find session by id {session_id}: {e}")
            raise

    def create_session(self, session: Session) -> Session:
        """Create a new session (alias for save without id)"""
        # Ensure it's a new session
        session.id = None
        session.is_ended = False
        session.ended_at = None
        return self.save(session)

    def end_session(self, session: Session) -> Session:
        """End an existing session"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE sessions 
                    SET is_ended = TRUE, ended_at = NOW()
                    WHERE id = %s
                    RETURNING id, user_id, content, is_ended, created_at, ended_at
                """, (session.id,))
                
                result = cur.fetchone()
                if result:
                    session.id = result[0]
                    session.user_id = result[1]
                    session.content = result[2]
                    session.is_ended = result[3]
                    session.created_at = result[4]
                    session.ended_at = result[5]
                
                self.db.commit()
                logger.info(f"Session {session.id} ended successfully")
                return session
                
        except psycopg2.Error as e:
            self.db.rollback()
            logger.error(f"Couldn't end session {session.id}: {e}")
            raise

    def find_active_sessions_by_user(self, user_id: int) -> list[Session]:
        """Find all active (not ended) sessions for a user"""
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, user_id, content, is_ended, created_at, ended_at
                    FROM sessions
                    WHERE user_id = %s AND is_ended = FALSE
                    ORDER BY created_at DESC
                """, (user_id,))
                
                results = cur.fetchall()
                sessions = []
                for result in results:
                    session = Session(
                        id=result['id'],
                        user_id=result['user_id'],
                        content=result['content'],
                        is_ended=result['is_ended'],
                        created_at=result['created_at'],
                        ended_at=result['ended_at']
                    )
                    sessions.append(session)
                
                return sessions
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find active sessions for user {user_id}: {e}")
            return []

    def find_sessions_by_user(self, user_id: int, limit: int = 10) -> list[Session]:
        """Find recent sessions for a user"""
        try:
            with self.db.get_cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT id, user_id, content, is_ended, created_at, ended_at
                    FROM sessions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                
                results = cur.fetchall()
                sessions = []
                for result in results:
                    session = Session(
                        id=result['id'],
                        user_id=result['user_id'],
                        content=result['content'],
                        is_ended=result['is_ended'],
                        created_at=result['created_at'],
                        ended_at=result['ended_at']
                    )
                    sessions.append(session)
                
                return sessions
                
        except psycopg2.Error as e:
            logger.error(f"Couldn't find sessions for user {user_id}: {e}")
            return []