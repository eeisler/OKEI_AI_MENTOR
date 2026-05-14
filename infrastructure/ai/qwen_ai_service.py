from typing import Dict, List

import ollama
from ollama import chat

from application.ports.ai.ai_port import AIService
from config.config import Config

config = Config.load()


class QwenAIService(AIService):
    async def get_ai_response_with_context(self, 
        user_id: int,
        user_message: str,
        context: List[Dict[str, str]]
        ) -> str:

        context_str = ""
        for msg in context:
            context_str += f"{msg['role']}: {msg['content']}\n"
        
        full_input = context_str + f"user: {user_message}"

        response = chat(
            model='qwen:0.5b',
            messages=[{'role': 'user', 'content': full_input}]
        )

        return response.message.content
    
    async def get_simple_response(self, user_text: str) -> str:
        response = chat(
            model='qwen:0.5b',
            messages=[{user_text}]
        )
        return response.message.content

    async def generate_task(self, prompt: str) -> str:
        response = chat(
            model='qwen:0.5b',
            messages=[{'role': 'system', 'content': config.ai_instruction},
                {'role': 'user', 'content': prompt}]
        )
        return f"{prompt}\n{response.message.content}"