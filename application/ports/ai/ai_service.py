from abc import ABC, abstractmethod


class AIService:
    @abstractmethod
    async def get_ai_response_with_context(
        self, 
        user_id: int,
        user_message: str
    ) -> str:
    pass

    @abstractmethod
    async def get_simple_response(self, user_message: str) -> str:
        pass
