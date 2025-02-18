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
