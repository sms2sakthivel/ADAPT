from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMInterface(ABC):
    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str, model_name: str, max_tokens: int = -1) -> str:
        pass

    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str, json_schema: BaseModel, model_name: str, max_tokens: int = -1) -> BaseModel:
        pass

