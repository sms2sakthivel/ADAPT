from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class Method(BaseModel):
    method: str
    description: str

class Specification(BaseModel):
    path: str
    method: str
    description: Optional[str] = None
    consumes: Optional[List[str]] = None
    produces: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    requests: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    definitions: Optional[Dict[str,Any]] = None


class MethodWithSpec(BaseModel):
    method: str
    description: str
    specification: Specification

class ExposedEndpoint(BaseModel):
    endpoint: str
    methods: list[Method]

class ExposedEndpointWithSpec(BaseModel):
    endpoint: str
    methods: list[MethodWithSpec]

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

    def add_specifications(self, specifications: List[Specification]) -> "OnboardingDataModelWithSpec":
        output = OnboardingDataModelWithSpec(
            exposed_endpoints= [],
            consumed_endpoints= self.consumed_endpoints,
            is_swagger_supported = self.is_swagger_supported,
            swagger_endpoint = self.swagger_endpoint,
            repository = self.repository,
            branch = self.branch,
            port = self.port,
            communication_protocol = self.communication_protocol,
            is_tls_supported = self.is_tls_supported,
        )
        print("Specification Output Object Created...")
        for endpoint in self.exposed_endpoints:
            endpoint_with_spec = ExposedEndpointWithSpec(endpoint=endpoint.endpoint, methods=[])
            for method in endpoint.methods:
                method_with_spec = MethodWithSpec(method=method.method, description=method.description, specification=Specification(path="", method=""))
                for specification in specifications:
                    if endpoint.endpoint == specification.path and method.method == specification.method:
                        method_with_spec.specification = specification
                        endpoint_with_spec.methods.append(method_with_spec)
                        break
            output.exposed_endpoints.append(endpoint_with_spec)

        return output

class OnboardingDataModelWithSpec(BaseModel):
    exposed_endpoints: list[ExposedEndpointWithSpec]
    consumed_endpoints: list[ConsumedEndpoint]
    is_swagger_supported: bool
    swagger_endpoint: str
    repository: Branch
    branch: Branch
    port: str
    communication_protocol: str
    is_tls_supported: bool


class SpecExtractionOutput(BaseModel):
    endpoints: List[Specification]

class ProjectDataModel(BaseModel):
    repository_url: str
    branch_name: str
