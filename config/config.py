# config.py
import os
from dataclasses import dataclass, field
from typing import Self

from dotenv import load_dotenv


class ConfigError(Exception):
    pass

class DbHostMissing(ConfigError):
    pass


@dataclass
class AIModelConfig:
    cloud_folder: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    base_url: str
    instruction: str = ""

    @classmethod
    def load(cls, prefix: str) -> Self:
        return cls(
            cloud_folder=os.getenv(f"{prefix}_YANDEX_CLOUD_FOLDER", ""),
            api_key=os.getenv(f"{prefix}_YANDEX_CLOUD_API_KEY", ""),
            model=os.getenv(f"{prefix}_YANDEX_CLOUD_MODEL", ""),
            temperature=float(os.getenv(f"{prefix}_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv(f"{prefix}_MAX_TOKENS", 500)),
            base_url=os.getenv(f"{prefix}_BASE_URL", ""),
            instruction=os.getenv(f"{prefix}_INSTRUCTIONS", ""),
        )


@dataclass
class Config:
    load_dotenv()
    mentor_ai: AIModelConfig      
    secondary_ai: AIModelConfig  

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    key: str
    redis: str
    task_generation_hour: int
    task_generation_minute: int
    task_generation_timezone: str


    @classmethod
    def load(cls) -> Self:

        instance = cls(
            mentor_ai=AIModelConfig.load("MENTOR"),
            secondary_ai=AIModelConfig.load("SECONDARY"),

            db_host=os.getenv("DB_HOST", ""),
            db_port=int(os.getenv("DB_PORT", 0)),
            db_name=os.getenv("DB_NAME", ""),
            db_user=os.getenv("DB_USER", ""),
            db_password=os.getenv("DB_PASSWORD", ""),

            key=os.getenv("SECRET_KEY", ""),

            redis=os.getenv("REDIS_URL"),
            task_generation_hour = int(os.getenv("TASK_GENERATION_HOUR", 0)),
            task_generation_minute = int(os.getenv("TASK_GENERATION_MINUTE", 0)),
            task_generation_timezone = os.getenv("TASK_GENERATION_TIMEZONE", "Asia/Yekaterinburg")
        )

        instance.validate()

        return instance

    def validate(self):
        pass
