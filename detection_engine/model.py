from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Method(BaseModel):
    method: str
    description: str

class AffectedEndpoint(BaseModel):
    endpoint: str
    methods: Method
    description: str
    reasoning: List[str]

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

class AffectedEndpointWithSpec(BaseModel):
    endpoint: str
    methods: Method
    description: str
    reasoning: List[str]
    specification_after_the_change: Specification

class EndpointWithSpec(BaseModel):
    endpoint: AffectedEndpoint
    specification: Specification

class Change(BaseModel):
    change_type: str
    affected_endpoint: List[AffectedEndpoint]

class ChangeWithSpecification(BaseModel):
    change_type: str
    affected_endpoint: List[EndpointWithSpec]

class ChangeWithUpdatedSpec(BaseModel):
    change_type: str
    affected_endpoint: List[AffectedEndpointWithSpec]

class AnalysisSummary(BaseModel):
    breaking_changes: List[Change]
    non_breaking_changes: List[Change]

class AnalysisSummaryWithSpecification(BaseModel):
    breaking_changes: List[ChangeWithUpdatedSpec]
    non_breaking_changes: List[ChangeWithUpdatedSpec]



class GitHubPRAnalysisOutput(BaseModel):
    pr_id: str
    analysis_summary: AnalysisSummary

    def add_specifications(self, pr_id: str, specifications: List[Specification]) -> "GitHubPRAnalysisOutputWithSpecification":
        output = GitHubPRAnalysisOutputWithSpecification(
            pr_id=pr_id,
            analysis_summary = AnalysisSummaryWithSpecification(
                breaking_changes=[],
                non_breaking_changes=[]
            )
        )
        for change in self.analysis_summary.breaking_changes:
            if len(output.analysis_summary.breaking_changes) == 0:
                output.analysis_summary.breaking_changes = []
            change_with_spec = ChangeWithSpecification(change_type=change.change_type, affected_endpoint=[])
            for endpoint in change.affected_endpoint:
                affected_endpoint_with_spec = EndpointWithSpec(endpoint=endpoint, specification=Specification(path="", method=""))
                for specification in specifications:
                    if endpoint.endpoint == specification.path and endpoint.methods.method == specification.method:
                        affected_endpoint_with_spec.specification = specification
                        change_with_spec.affected_endpoint.append(affected_endpoint_with_spec)
                        break
            output.analysis_summary.breaking_changes.append(change_with_spec)

        for change in self.analysis_summary.non_breaking_changes:
            if len(output.analysis_summary.non_breaking_changes) == 0:
                output.analysis_summary.non_breaking_changes = []
            change_with_spec = ChangeWithSpecification(change_type=change.change_type, affected_endpoint=[])
            for endpoint in change.affected_endpoint:
                affected_endpoint_with_spec = EndpointWithSpec(endpoint=endpoint, specification=Specification(path="", method=""))
                for specification in specifications:
                    if endpoint.endpoint == specification.path and endpoint.methods.method == specification.method:
                        affected_endpoint_with_spec.specification = specification
                        change_with_spec.affected_endpoint.append(affected_endpoint_with_spec)
                        break
            output.analysis_summary.non_breaking_changes.append(change_with_spec)
        return output

class GitHubPRAnalysisOutputWithSpecification(BaseModel):
    pr_id: str
    analysis_summary: AnalysisSummaryWithSpecification

class SpecExtractionOutput(BaseModel):
    endpoints: List[Specification]

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
    analysis_summary: AnalysisSummaryWithSpecification
    is_approved: bool

