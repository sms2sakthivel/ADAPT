from pydantic import BaseModel
from typing import List


class Method(BaseModel):
    method: str
    description: str

class AffectedEndpoint(BaseModel):
    endpoint: str
    methods: Method
    description: str
    reasoning: List[str]

class Change(BaseModel):
    change_type: str
    affected_endpoint: List[AffectedEndpoint]

class AnalysisSummary(BaseModel):
    breaking_changes: List[Change]
    non_breaking_changes: List[Change]

class GitHubPRAnalysisOutput(BaseModel):
    pr_id: str
    analysis_summary: AnalysisSummary

# class EndpointWithSpec(BaseModel):
#     endpoint: AffectedEndpoint
#     specification: dict

class EndpointWithSpecs(BaseModel):
    endpoint: AffectedEndpoint
    specification: dict
    existing_specification: dict

class JIRATicketExtractionOutput(BaseModel):
    ticket_id: str
    identified_endpoints: List[AffectedEndpoint]

class JIRATicketAnalysisInput(BaseModel):
    ticket_id: str
    endpoint_with_specs: List[EndpointWithSpecs]

class JIRATicketAnalysisOutput(BaseModel):
    ticket_id: str
    analysis_summary: AnalysisSummary
    is_approved: bool