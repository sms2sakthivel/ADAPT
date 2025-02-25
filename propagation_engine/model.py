from pydantic import BaseModel
from typing import Optional, List

class GithubProject(BaseModel):
    repository: str
    branch: str
    prId: Optional[str]
    prUrl: Optional[str]

class JiraProject(BaseModel):
    url: str
    id: str
    ticketId: Optional[str]
    ticketUrl: Optional[str]

class AffectedClient(BaseModel):
    name: str
    guid: str
    githubProject: Optional[GithubProject]
    jiraProject: Optional[JiraProject]

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

class ActionItemsResponse(BaseModel):
    actionItems: List[ActionItem]


class PullRequest(BaseModel):
    title: str
    description: str

class GithubPRCodeGenerationOutput(BaseModel):
    branch: str
    diff_string: str
    commit_message: str
    pull_request: PullRequest

class Reference(BaseModel):
    title: str
    url: str

class JiraTicketGenerationOutput(BaseModel):
    title : str
    summary: str
    description: str
    issue_type: str
    priority: str
    severity: str
    affected_endpoint: str
    impact: str
    required_changes: str
    definition_of_ready: str
    definition_of_done: str
    references: Optional[List[Reference]]

class InputGithubProject(BaseModel):
    prId: Optional[str] = None
    prUrl: Optional[str] = None

class InputJiraProject(BaseModel):
    ticketId: Optional[str] = None
    ticketUrl: Optional[str] = None

class InputAffectedClient(BaseModel):
    githubProject: Optional[InputGithubProject] = None
    jiraProject: Optional[InputJiraProject] = None