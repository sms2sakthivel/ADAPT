from pydantic import BaseModel
from enum import Enum

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

