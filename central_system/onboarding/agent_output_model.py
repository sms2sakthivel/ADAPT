from pydantic import BaseModel


class Method(BaseModel):
    method: str
    description: str
    specification: dict


class ExposedEndpoint(BaseModel):
    endpoint: str
    methods: list[Method]


class ConsumedEndpoint(BaseModel):
    endpoint: str
    methods: list[Method]
    port_config: str
    port: int

class Branch(BaseModel):
    project_name: str
    guid: str
    description: str
    jira_instance_url: str
    jira_project_key: str


class OnboardingDataModel(BaseModel):
    exposed_endpoints: list[ExposedEndpoint]
    consumed_endpoints: list[ConsumedEndpoint]
    is_swagger_supported: bool
    swagger_endpoint: str
    repository: Branch
    branch: Branch
    port: str
    communication_protocol: str
    is_tls_supported: bool


class ProjectDataModel(BaseModel):
    repository_url: str
    branch_name: str
