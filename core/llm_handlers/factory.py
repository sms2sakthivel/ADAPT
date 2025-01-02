from .interface import LLMInterface
from .openai_handler import OpenAIHandler
from .lmstudio_handler import LMStudioHandler

def create_llm_handler(provider: str, api_key: str, api_url: str = None) -> LLMInterface:
    if provider == "openai":
        return OpenAIHandler(api_key)
    elif provider == "lmstudio":
        return LMStudioHandler(api_url)
    else:
        raise ValueError(f"Unknown provider: {provider}")