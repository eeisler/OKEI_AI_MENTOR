from application.ports.ai.ai_port import AIService
from application.services.session_service import SessionService
from application.services.skill_matrix_service import SkillMatrixService
from application.services.student_progress import StudentProgressService
from domain.entities.user import User
from domain.entities.study import Specialties
from domain.entities.student_progress import StudentProgress
import re

logger = logging.getLogger(__name__)

class AISessionService:
    def __init__(
        self,
        ai_service: AIService,
        dialog_service: DialogService,
        session_service: SessionService,
        matrix_service: SkillMatrixService,
        student_progress_service: StudentProgressService,
        instruction: str
    ):
        self.ai_service = ai_service
        self.dialog_service = dialog_service
        self.session_service = session_service
        self.student_progress_service = student_progress_service
        self.matrix_service = matrix_service
        self.instruction = instruction

    async def start_session(self, user_id: int, user_message: str):
        prompt = self.form_question_instruction(user_id=user_id)
        ai_response = await self.ai_service.generate_task(prompt=prompt)
        session = await self.session_service.create_session(user_id=user_id, content=ai_response)
        return session
    
    def continue_session(self, session_id: int): 
        session = self.session_service.find_by_id(session_id)        
        return session 
    
    def form_question_instruction(self, user_id: int) -> str:        
        user: User = self.student_progress_service.get_user(user_id)
        course: int = user.get_course()
        specialization: Specialties = self.matrix_service.get_specialization(user_id)

        matrix_skill_id: int = self.student_progress_service.get_task_id(user_id)
        matrix_skill: str = self.matrix_service.get_task(matrix_skill_id)  
        matrix_criterion: str = self.matrix_service.get_criterions(matrix_skill_id) 
        student_progress: int = self.student_progress_service.get_student_level(user_id)
        weaknesses: str = self.student_progress_service.get_weaknesses(user_id)

        question_instruction = (f"""{self.instruction}
                                Сделай задание для отработки навыка {matrix_skill} для студента
                                специальности {specialization} {course} курса
                                с прогрессом по этому навыку - {student_progress}% и с 
                                проблемами усвоения темы в следующих местах: {weaknesses}
                                Навык считается освоенным когда: {matrix_criterion}""")

        return question_instruction

    async def save_session(self, session_id: int):
        session = self.session_service.find_by_id(session_id)

        if session.is_ended:
            student_progress: StudentProgress = self.student_progress_service.find_by_id(session.user_id)
            results = self.get_session_result(session)
            student_progress.level = results['percentage']
            student_progress.weaknesses = results['weaknesses']
            await self.student_progress_service.save(student_progress)
            await self.session_service.save(session)
        else:
            await self.session_service.save(session)

    def _parse_ai_result(self, ai_response: str):
        ai_response = ai_response.strip()
        percentage = re.search(r'^(\d{1,3})', ai_response)
        weaknesses = ai_response[percentage.end():].strip()
        weaknesses = re.sub(r'^[%\s-]+', '', weaknesses)
        return percentage, weaknesses

    def get_session_result(self, session: Session):
        user_id: int = self.session_service.get_user(session_id)
        matrix_skill_id: int = self.student_progress_service.get_task_id(user_id)
        criterions: str = self.matrix_service.get_criterions(matrix_skill_id)
        result_instruction =  f"""Оцени усвоение темы студентом по стобалльной шкале.
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
        
        ai_answer = self.ai_service.get_simple_response(user_message=session.content)
        
        progress, weaknesses = self._parse_ai_result(ai_answer)

        result = {
            'progress': progress,
            'weaknesses': weaknesses
        }

        return result