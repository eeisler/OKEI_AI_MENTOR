from application.services.dialog_service import DialogService
from infrastructure.repositories.dialog_repository import DialogRepository
from application.ports.ai.ai_port import AIService

from domain.entities.dialog import Dialog


class AIContextService:
    def __init__(
            self, 
            dialog_service: DialogService,
            dialog_repository: DialogRepository,
            ai_service: AIService,
            matrix_repository: SkillMatrixRepository,
            student_progress_repository: StudentProgressRepository,
            user_repository: UserRepository,
            instruction: str
            ):
        self.dialog_service = dialog_service
        self.ai_service = ai_service
        self.instruction = instruction
        self.student_progress_repository = student_progress_repository
        self.matrix_repository = matrix_repository
        self.user_repository = user_repository

    async def get_response_with_history(self, user_id: int, user_message: str):
        dialog_history = await self.dialog_service.get_user_history(user_id, limit=10)

        return await self.ai_service.get_ai_response_with_context(
            user_id=user_id,
            user_message=user_message,
            context=dialog_history
        )
        
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

    def get_student_result(self, dialog: Dialog):
        user_id: int = self.dialog_service.find_by_id(dialog.id).user_id
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

