import openai
from config import Config
from services.db_service import db_service  


config = Config.load()

class AIService:
    def __init__(self):
        self.api_key = config.ai_api_key
        self.model = config.ai_model
        self.base_url = config.ai_base_url
        self.project = config.ai_cloud_folder
        self.temperature = config.ai_temperature
        self.max_tokens = config.ai_max_tokens
        self.instruction = config.ai_instructoon
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            project=self.project
        )

    def get_ai_response_with_context(self, user_id: int, user_text: str):
        history = db_service.get_recent_dialogs(user_id, limit=10)
        
        messages = []
        messages.append({
            "role": "system",
            "content": self.instruction
        })
        
        messages.extend(history)
        
        messages.append({
            "role": "user",
            "content": user_text
        })
        
        response = self.client.responses.create(
            model=f"gpt://{self.project}/{self.model}",
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=messages 
        )
        
        return response.output_text

    def get_ai_response(self, input):
        response = self.client.responses.create(
            model=f"gpt://{self.project}/{self.model}",
            temperature=self.temperature,
            instructions=self.instruction,
            input=input,
            max_output_tokens=self.max_tokens
        )
        
        return response.output_text

ai_service = AIService()