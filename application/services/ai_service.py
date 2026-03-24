from application.ports.repositories import DialogRepository
from application.ports.ai import AIService


class AIContextService:
    def __init__(
            self, 
            dialog_repository: DialogRepository,
            ai_service: AIService
            instruction: str
            ):
        self.dialog_repository = dialog_repository
        self.ai_service = ai_service
        self.instruction = instruction

    async def get_response_with_history(self, user_id: int, user_message: str):
        dialog_history = await self.dialog_repository.get_recent_dialogs(user_id, limit=10)
        
        messages_history = []

        for dialog in dialog_history:
            messages_history.extend(dialog.to_context_messages())

        messages = [
            {'role': 'system', 'content': self.instruction},
            *messages_history,
            {'role': 'user', 'content': user_message}
        ]
        
        return await self.ai_service.get_ai_response_with_context(
            user_id=user_id,
            user_message=user_message,
            history=messages
        )
