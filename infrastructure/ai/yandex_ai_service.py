from typing import Dict, List

import openai

from application.ports.ai import AIService
from config.config import Config


class YandexAIService(AIService):
    def __init__(self, config: Config):
        self.client = openai.OpenAI(
            ai_api_key=config.ai_api_key,
            ai_base_url=config.ai_base_url,
            project=config.ai_cloud_folder
        )
        self.ai_model = config.ai_model
        self.ai_temperature = config.ai_temperature
        self.ai_max_tokens = config.ai_max_tokens
        self.ai_instructoon = config.ai_instructoon

    async def get_ai_response_with_context(self, 
        user_id: int,
        user_message: str,
        history: List[Dict[str, str]]
        ) -> str:
        response = self.client.responses.create(
            model=f"gpt://{self.client.project}/{self.model}",
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=history  
        )
        return response.output_text
    
    async def get_simple_response(self, user_text: str) -> str:
        response = self.client.responses.create(
            model=f"gpt://{self.client.project}/{self.model}",
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=user_text
        )
        return response.output_text