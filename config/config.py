#config.py
import os
from dataclasses import dataclass
from typing import Self
from dotenv import load_dotenv


class ConfigError(Exception):
    pass

class BotTokenMissing(ConfigError):
    pass

class DbHostMissing(ConfigError):
    pass


@dataclass
class Config:
    bot_token: str
    
    ai_cloud_folder: str
    ai_api_key: str
    ai_model: str
    ai_temperature: float
    ai_max_tokens: int
    ai_base_url: str
    ai_instruction: str

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    key: str

    @classmethod
    def load(cls) -> Self:
        load_dotenv() 
        bot_token = os.getenv('BOT_TOKEN', '')
        
        ai_cloud_folder = os.getenv('YANDEX_CLOUD_FOLDER', '')
        ai_api_key = os.getenv('YANDEX_CLOUD_API_KEY', '')
        ai_model = os.getenv('YANDEX_CLOUD_MODEL', '')
        ai_temperature = float(os.getenv('AI_TEMPERATURE', 0.7))
        ai_max_tokens = int(os.getenv('AI_MAX_TOKENS', 500))
        ai_base_url = os.getenv('AI_BASE_URL', '')
        ai_instruction = os.getenv('INSTRUCTIONS', '')

        db_host = os.getenv('DB_HOST', '')
        db_port = int(os.getenv('DB_PORT', 0))
        db_name = os.getenv('DB_NAME', '')
        db_user = os.getenv('DB_USER', '')
        db_password = os.getenv('DB_PASSWORD', '')

        key = os.getenv('SECRET_KEY', '')

        instance = cls(
            bot_token = bot_token,
            ai_cloud_folder = ai_cloud_folder,
            ai_api_key = ai_api_key,
            ai_model = ai_model,
            ai_temperature = ai_temperature,
            ai_max_tokens = ai_max_tokens,
            ai_base_url = ai_base_url,
            ai_instruction = ai_instruction,
            db_host = db_host,
            db_port = db_port,
            db_name = db_name,
            db_user = db_user,
            db_password = db_password,
            key=key
        )

        #instance.validate()

        return instance

    # def validate(self):
    #     if not self.bot_token:
    #         raise BotTokenMissing
    #     if not self.db_host:
    #         raise DbHostMissing