from application.repositories.dialog import DialogRepository
from application.ports.ai.ai_port import AIService


class AIContextService:
    def __init__(
            self, 
            dialog_service: DialogService,
            ai_service: AIService,
            instruction: str
            ):
        self.dialog_service = dialog_service
        self.ai_service = ai_service
        self.instruction = instruction

    async def get_response_with_history(self, user_id: int, user_message: str):
        dialog_history = await self.dialog_service.get_user_history(user_id, limit=10)
        
        return await self.ai_service.get_ai_response_with_context(user_message=user_message)
        

