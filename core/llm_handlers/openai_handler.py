from openai import OpenAI
from pydantic import BaseModel
from .interface import LLMInterface

class OpenAIHandler(LLMInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_text(self, system_prompt: str, user_prompt: str, model_name:str = "gpt-4o-mini", max_tokens: int = -1) -> str:
        response = self.client.Completion.create(
            model= model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                { "role": "user","content": user_prompt}
            ]
        )
        return response.choices[0].message
    
    def generate_json(self, system_prompt: str, user_prompt: str, json_schema: BaseModel, model_name:str = "gpt-4o-mini", max_tokens: int = -1) -> BaseModel:
        response = self.client.beta.chat.completions.parse(
            model= model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                { "role": "user","content": user_prompt}
            ],
            response_format = json_schema
        )

        response = response.choices[0].message
        if (response.refusal):
            print(response.refusal)
            return None
        else:
            parsed = response.parsed
        return parsed