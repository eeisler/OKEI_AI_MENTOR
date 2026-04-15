# ai_session_service.py

from application.ports.ai.ai_port import AIService
from application.repositories.session_repository import SessionRepository
from application.repositories.skill_matrix_repository import SkillMatrixRepository
from application.repositories.student_progress_repository import StudentProgressRepository
from application.repositories.user_repository import UserRepository
from domain.entities.user import User
from domain.entities.study import Specialties
from domain.entities.student_progress import StudentProgress
from domain.entities.session import Session
import re
import logging
from datetime import datetime 

logger = logging.getLogger(__name__)

class AISessionService:
    def __init__(
        self,
        ai_service: AIService,
        matrix_repository: SkillMatrixRepository,
        student_progress_repository: StudentProgressRepository,
        user_repository: UserRepository,
        instruction: str
    ):
        self.ai_service = ai_service
        self.session_repository = session_repository
        self.student_progress_repository = student_progress_repository
        self.matrix_repository = matrix_repository
        self.instruction = instruction
        self.user_repository = user_repository

    async def start_session(self, user_id: int):
        prompt = self.form_question_instruction(user_id=user_id)
        ai_response = await self.ai_service.generate_task(prompt=prompt)
        created_at = datetime.now()

        session = Session(
            user_id=user_id, 
            content=ai_response,
            is_ended=False,
            created_at=created_at
        )
        session = await self.session_repository.create_session(session)
        return session
    
    def continue_session(self, session_id: int, user_message:str) -> str: 
        session = self.session_repository.find_by_id(session_id)     

        ai_response = await self.ai_service.get_response_with_history(
            user_id=session.user_id, 
            user_message=user_message)
        
        is_ended: bool = self.evaluate(ai_response)
        if is_ended:
            session.is_ended = True
            self.save_session(session_id)
            logger.info("Session ended and saved")
            return None

        return ai_response 
    
    def evaluate(self, ai_response: str) -> bool:
        

    def form_question_instruction(self, user_id: int) -> str:        
        user: User = self.user_repository.find_by_id(user_id)
        course: int = user.course

        matrix_skill_id: int = self.student_progress_repository.find_by_id(user_id).skill_id
        matrix_skill: str = self.matrix_repository.find_by_id(matrix_skill_id).skill 
        matrix_criterion: str = self.matrix_repository.find_by_id(matrix_skill_id).criterions
        student_progress: int = self.student_progress_repository.find_by_id(user_id).student_level
        weaknesses: str = self.student_progress_repository.find_by_id(user_id).weaknesses
        Specialty: Specialty = self.matrix_repository.find_by_id(matrix_skill_id).Specialty

        question_instruction = (f"""{self.instruction}
                                Сделай задание для отработки навыка {matrix_skill} для студента
                                специальности {Speciality} {course} курса
                                с прогрессом по этому навыку - {student_progress}% и с 
                                проблемами усвоения темы в следующих местах: {weaknesses}
                                Навык считается освоенным когда: {matrix_criterion}""")

        return question_instruction

    async def save_session(self, session_id: int):
        session = self.session_repository.find_by_id(session_id)

        if session.is_ended:
            student_progress: StudentProgress = self.student_progress_repository.find_by_id(session.user_id)
            results = self.get_session_result(session)  
            student_progress.level = results['percentage']
            student_progress.weaknesses = results['weaknesses']
            await self.student_progress_repository.save(student_progress)
            await self.session_repository.save(session)
        else: 
            await self.session_repository.save(session)

    def _parse_ai_result(self, ai_response: str):
        ai_response = ai_response.strip()
        match = re.search(r'^(\d{1,3})', ai_response)
        if not match:
            logger.warning(f"Failed to parse percentage from: {ai_response}")
            return None, ai_response
        percentage = int(match.group(1))
        weaknesses = ai_response[match.end():].strip()
        weaknesses = re.sub(r'^[%\s-]+', '', weaknesses)
        return percentage, weaknesses

    def get_session_result(self, session: Session):
        user_id: int = self.session_repository.find_by_id(session.id).user_id
        matrix_skill_id: int = self.student_progress_repository.find_by_id(user_id).skill_id
        criterions: str = self.matrix_repository.find_by_id(matrix_skill_id).criterions  
        result_instruction =  f"""Оцени усвоение темы студентом по стобалльной шкале. 
                                Процент освоения считай только по первому ответу студента.
                                Последующие сообщения используй для определения слабостей студента в теме.
                                Критерии усвоения: {criterions}

                                Формат ответа (строго соблюдай):
                                [Число от 1 до 100]%
                                - [Слабость 1]
                                - [Слабость 2]
                                - [Слабость 3]
                                (добавь столько пунктов, сколько необходимо)

                                Пример:
                                65%
                                - не понимает синтаксис функций в Python
                                - путает параметры и аргументы
                                - не использует return правильно"""
        
        content = session.content + result_instruction

        ai_answer = self.ai_service.get_simple_response(user_message=content)  
        
        progress, weaknesses = self._parse_ai_result(ai_answer)

        result = {
            'progress': progress,
            'weaknesses': weaknesses
        }

        return result

    def end_session(self, session_id):
        session = self.session_repository.find_by_id(session_id)
        session.is_ended = True
        session.ended_at = datetime.now()
        return self.session_repository.save(session)