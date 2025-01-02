import requests
import json
from typing import Optional
from pydantic import BaseModel

from .interface import LLMInterface

class Message(BaseModel):
    role: str
    content: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str
    logprobs: Optional[dict]

class LMStudioRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float
    max_tokens: int
    stream: bool

class LMStudioResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[Choice]
    usage: Usage
    system_fingerprint: str

    def content_json(self) -> dict:
        stripped_content = self.choices[0].message.content.strip('```json')
        return json.loads(stripped_content)

class LMStudioHandler(LLMInterface):
    def __init__(self, api_url: str):
        self.api_url = api_url
    
    def generate_text(self, system_prompt:str, user_prompt: str, model_name: str, max_tokens: int = -1) -> str:
        headers = {"content-type":"application/json"}
        body = LMStudioRequest(model= model_name,
                        stream=False,
                        messages=[Message(role="system", content=system_prompt),Message(role="user", content=user_prompt)],
                        temperature=0.7,
                        max_tokens=max_tokens)
        response = requests.post(self.api_url, headers=headers, data=body.json())
        json_response = response.json()
        lm_studio_response = LMStudioResponse(**json_response)
        return lm_studio_response.choices[0].message.content

    def generate_json(self, system_prompt: str, user_prompt: str, json_schema: BaseModel, model_name: str, max_tokens: int = -1) -> BaseModel:
        headers = {"content-type":"application/json"}
        body = LMStudioRequest(model= model_name,
                        stream=False,
                        messages=[Message(role="system", content=system_prompt),Message(role="user", content=user_prompt)],
                        temperature=0.7,
                        max_tokens=max_tokens)
        response = requests.post(self.api_url, headers=headers, data=body.json())
        json_response = response.json()
        lm_studio_response = LMStudioResponse(**json_response)
        content = lm_studio_response.content_json()
        parsed_json_schema_obj = json_schema.model_validate(content)
        return parsed_json_schema_obj


