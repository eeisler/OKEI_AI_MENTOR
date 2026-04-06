import psycopg2
from psycopg2 import extras
from contextlib import contextmanager
from config import config


class DataBaseConnection:
    def __init__(self, config):
        self.config = config
        self.connection_params = {
            'host': config.db_host,
            'port': config.db_port,
            'database': config.db_name,
            'user': config.db_user,
            'password': config.db_password
        }
        self._connection = None

    def connect(self):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(**self.connection_params)
        return self._connection

    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    @contextmanager
    def get_cursor(self, cursor_factory=None):
        connection = self.connect()
        cursor = connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()

    def commit(self):
        if self._connection and not self._connection.closed:
            self._connection.commit()

    def rollback(self):
        if self._connection and not self._connection.closed:
            self._connection.rollback()