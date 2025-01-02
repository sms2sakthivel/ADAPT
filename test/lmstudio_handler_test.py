import os
from pydantic import BaseModel
from enum import Enum
import json

from core.llm_handlers.template_to_prompt import generate_prompt_from_template, get_system_prompt
from core.llm_handlers.factory import create_llm_handler


class PortConfig(Enum):
    dynamic = "dynamic"
    static = "static"

class Methods(BaseModel):
    method: str
    description: str

class ExposedEndpoints(BaseModel):
    endpoint: str
    methods: list[Methods]

class ConsumedEndpoints(BaseModel):
    endpoint: str
    methods: list[Methods]
    port_config: PortConfig
    port: str

class OnboardingSchema(BaseModel):
    exposed_endpoints: list[ExposedEndpoints]
    consumed_endpoints: list[ConsumedEndpoints]
    is_swagger_supported: bool
    swagger_endpoint: str
    project_name: str
    project_guid: str
    port: str
    communication_protocol: str
    is_tls_supported: bool



if __name__ == "__main__":
    # Step 1: Define the template and repository details
    template = "/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/ADAPT/central-system/onboarding/prompt_templates/extract_onboarding_informations.json"
    repository = "sms2sakthivel/payment-manager"
    branch = "master"
    included_extensions = [".go", ".project.json"]

    # Step 2: Create the OpenAIHandler with your API key
    lm_studio_handler = create_llm_handler(provider="lmstudio", api_url=os.environ["LMSTUDIO_CHAT_COMPLETION_URL"], api_key="")

    # Step 3: Generate the system prompt and user prompt
    system_prompt = get_system_prompt(template)
    user_prompt = generate_prompt_from_template(template, repo=repository, branch=branch, included_extensions=included_extensions)
    model_name = "qwen2.5-coder-7b-instruct"
    
    # Step 4: Generate the JSON response using the OpenAIHandler
    response:OnboardingSchema = lm_studio_handler.generate_json(system_prompt=system_prompt, user_prompt=user_prompt, json_schema=OnboardingSchema,  model_name=model_name)
    print(json.dumps(json.loads(response.json()), indent=4))
