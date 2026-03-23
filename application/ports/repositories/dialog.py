from abc import ABC, abstractmethod

import psycopg2
from config import Config
import logging


config = Config.load()


class DialogRepository(ABC):
    @abstractmethod
    def save(self, dialog: Dialog):
        pass

    @abstractmethod
    def get_recent_dialogs(self, user_id):
        pass
