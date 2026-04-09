#main.py
import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import BasicAuth
from dotenv import load_dotenv

from application.repositories.session_repository import SessionRepository
from application.repositories.skill_matrix_repository import SkillMatrixRepository
from application.repositories.student_progress_repository import StudentProgressRepository
from config.config import Config

from infrastructure.database.connection import DataBaseConnection
from infrastructure.repositories.postgres_student_progress_repository import PostgresStudentProgressRepository
from infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from infrastructure.repositories.postgres_dialog_repository import PostgresDialogRepository
from infrastructure.repositories.postgres_skill_matrix_repository import PostgesSkillMatrixRepository
from infrastructure.repositories.postgres_session_repository import PostgresSessionRepository
from infrastructure.repositories.postgres_specialty_repository import PostgresSpecialityRepository
from infrastructure.repositories.postgress_department_repository import PostgresDepartmentRepository

from infrastructure.ai.yandex_ai_service import YandexAIService
from application.services.ai_service import AIContextService
from application.services.user_service import UserService
from application.services.dialog_service import DialogService

from domain.entities.session import Session
from domain.entities.skill_matrix import SkillMatrix
from domain.entities.student_progress import StudentProgress
from domain.entities.user import User, UserRole
from domain.entities.study import Speciality, Department, Groups

from presentation.tg.start import router as start_router   
from presentation.tg.help import router as help_router 

from presentation.tg.message import MessageHandler

load_dotenv()
config = Config.load()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def setup_repositories(db: DataBaseConnection):
    return {
        'user': PostgresUserRepository(db),
        'dialog': PostgresDialogRepository(db),
        'skill_matrix': PostgesSkillMatrixRepository(db),
        'student_progress': PostgresStudentProgressRepository(db),
        'session': PostgresSessionRepository(db),
        'speciality': PostgresSpecialityRepository(db),
        'department': PostgresDepartmentRepository(db)
    }

def setup_services(repositories, config: Config):
    yandex_ai = YandexAIService(config)

    ai_context_service = AIContextService(
        dialog_service=DialogService(repositories['dialog']),
        ai_service=yandex_ai,
        instruction=config.ai_instruction
    )

    ai_session_service = AISessionService(
        ai_service=yandex_ai,
        session_repository=repositories['session'],
        matrix_repository=repositories['skill_matrix'],
        student_progress_repository=repositories['student_progress'],
        user_repository=repositories['user'],
        instruction=config.ai_instruction
    )

    return {
        'user': UserService(repositories['user'], repositories['skill_matrix'], repositories['student_progress']),
        'dialog': DialogService(repositories['dialog']),
        'ai_context': ai_context_service,
        'ai_session':ai_session_service
    }

def load_test_data():
    department = Department(
        name = "Отделение программирования"
    )

    speciality = Speciality(
        code = "09.07.02",
        short_name = "пк"
        full_name = "программист"
        department = department
    )

    group = Groups(
        course=3,
        specialty=speciality,
        group_number=1,
        is_active=True
    )

    user = User(
        first_name="Иванка"
        middle_name="Пупкина"
        last_name="Акакиевна"
        role=UserRole.STUDENT
        group=group
    )

    skill = SkillMatrix(
        speciality = speciality,
        course = 3,
        skill = "ООП на питоне",
        description = """
        Студент должен понимать и уметь применять основные принципы объектно-ориентированного программирования 
        в языке Python. Включает в себя создание классов и объектов, использование наследования, 
        инкапсуляции и полиморфизма. Студент должен уметь проектировать иерархии классов, 
        работать с магическими методами, понимать разницу между классом и экземпляром, 
        уметь использовать статические методы и методы класса, а также применять композицию и агрегацию.
        """,
        criterions = """
        Критерии освоения навыка (100%):
        
        1. Студент самостоятельно создает классы с атрибутами и методами (без ошибок синтаксиса)
        2. Корректно использует конструктор __init__ и self
        3. Применяет наследование: создает дочерние классы и переопределяет методы родителя
        4. Использует super() для вызова методов родительского класса
        5. Понимает и применяет инкапсуляцию: использует _ и __ для защиты атрибутов
        6. Создает property и setter для управления доступом к атрибутам
        7. Использует полиморфизм: разные классы с одинаковыми интерфейсами методов
        8. Работает с магическими методами (__str__, __repr__, __eq__, __lt__ и др.)
        9. Различает и применяет статические методы (@staticmethod) и методы класса (@classmethod)
        10. Проектирует композицию и агрегацию между классами
        11. Пишет тесты для проверки функциональности классов
        12. Отлавливает и обрабатывает исключения в ООП-коде
        13. Использует аннотации типов в определениях классов
        
        Шкала оценки:
        - 90-100%: Выполнены все критерии, код чистый и документированный
        - 70-89%: Основные критерии выполнены, есть небольшие пробелы
        - 50-69%: Базовые критерии выполнены, но есть существенные проблемы
        - 0-49%: Недостаточное понимание ООП в Python
        """
    )

    return {
        'user': user, 
        'department': department,
        'speciality': speciality,
        'group':group,
        'skill':skill
    }

async def main():
    config = Config.load()
    logger.info("Configuration loaded")
    
    db = DataBaseConnection(config)
    db.connect()
    logger.info("Database connected")
    
    repositories = setup_repositories(db)
    logger.info("Repositories created")
    
    services = setup_services(repositories, config)
    logger.info("Services created")
    
    # handlers = setup_handlers(services, config)
    # logger.info("Handlers created")
    data = load_test_data()    

    user = repositories['user'].save(data['user'])
    skill_matrix = repositories['skill_matrix'].save(data['skill'])
    department = repositories['department'].save(data['department'])
    speciality = repositories['speciality'].save(data['speciality'])

    ai_service = services['ai_context']
    ai_session = services['ai_session']

    session = async ai_session.start_session(user_id=user.id)

    task = await ai_service.get_response_with_history(user_id=1, user_message=user_message)
    user_message = input("User answer: ")

    print(session)

if __name__ == "__main__":
    asyncio.run(main())
