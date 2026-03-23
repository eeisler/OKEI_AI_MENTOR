from application.ports.repositories import DialogRepository
from application.ports.ai import AIService


class AIService:
    def __init__(
            self, 
            dialog_repository: DialogRepository,
            ai_service: AIService
            ):
        self.dialog_repository = dialog_repository
        self.ai_service = ai_service

    async def get_ai_response_with_context(self, user_id: int, user_message: str, instruction: str):
        dialog_history = await self.dialog_repository.get_recent_dialogs(user_id, limit=10)
        
        messages_history = []

        for dialog in dialog_history:
            messages_history.extend(dialog.to_context_messages())

        messages = [
            {'role': 'system', 'content': instruction},
            *messages_history,
            {'role': 'user', 'content': user_message}
        ]
        
        return await self.ai_service.get_ai_response_with_context(
            user_id=user_id,
            user_message=user_message,
            history=messages
        )

