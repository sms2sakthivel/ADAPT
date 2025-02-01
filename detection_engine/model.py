from pydantic import BaseModel
from typing import List


class Method(BaseModel):
    method: str
    description: str


class Endpoint(BaseModel):
    endpoint: str
    methods: list[Method]


class Change(BaseModel):
    change_type: str
    affected_endpoint: List[Endpoint]
    description: str
    reasoning: List[str]
    file_path: List[str]
    language: List[str]
    framework: List[str]


class AnalysisSummary(BaseModel):
    breaking_changes: List[Change]
    non_breaking_changes: List[Change]


class GitHubPRAnalysisOutput(BaseModel):
    pr_id: str
    analysis_summary: AnalysisSummary
