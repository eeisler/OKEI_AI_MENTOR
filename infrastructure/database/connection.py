from config.config import Config
import logging
from exceptions import *
import psycopg2

logger = logging.getLogger(__name__)

class DataBaseConnection:
    def __init__(self, config: Config):
        self.connection_params = {
            'host': config.db_host,
            'port': config.db_port,
            'database': config.db_name,
            'user': config.db_user,
            'password': config.db_password
        }
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(**self.connection_params)
                logger.info("DB connected")
            except psycopg2.Error as e:
                logger.error("DB connection faled")
                raise DataBaseConnectionError()
        return self.conn
    
    def close(self):
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
                logger.info('Connections closed succsessfuly')
            except psycopg2.Error as e:
                logger.error('Closing connection failed')

    def get_cursor(self, cursor_factory=None):
        if self.conn is None or self.conn.closed:
            logger.error('Getting cursor with no db connection')
            raise DataBaseConnectionError()

        if cursor_factory:
            return self.conn.cursor(cursor_factory=cursor_factory)

        return self.conn.cursor()

    def commit(self):
        try:
            self.conn.commit()
            logger.info('Commit done')
        except psycopg2.Error as e:
            logger.error('Db commit error')
            raise DataBaseCommitError

    def rollback(self):
        try:
            self.conn.rollback()
            logger.info('Rollback successfully') 
        except psycopg2.Error as e:
            logger.error('Rollback failed')
            raise RollbackError()
