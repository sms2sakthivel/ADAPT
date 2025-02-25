from typing import Optional
from pydantic import BaseModel

class GithubProject(BaseModel):
    prId: Optional[str] = None
    prUrl: Optional[str] = None

class JiraProject(BaseModel):
    ticketId: Optional[str] = None
    ticketUrl: Optional[str] = None

class AffectedClient(BaseModel):
    githubProject: Optional[GithubProject] = None
    jiraProject: Optional[JiraProject] = None

class AffectedEndpoint(BaseModel):
    id: Optional[str]
    url: str
    method: str
    changeType: str
    description: str
    reason: str
    changeOrigin: str
    originUniqueID: str
    changeOriginURL: str
    currentSpecification: str
    specificationAfterTheChange: str
    status: Optional[str]

class OriginatingService(BaseModel):
    name: str
    guid: str
    githubProject: Optional[GithubProject]
    jiraProject: Optional[JiraProject]
    affectedEndpoint: AffectedEndpoint

class ActionItem(BaseModel):
    id: str
    type: str
    comments: Optional[str]
    propagationStatus: str
    originatingService: OriginatingService
    affectedClient: AffectedClient


class MetaData(BaseModel):
    client : Optional[AffectedClient] = None

