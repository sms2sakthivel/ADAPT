import os
from typing import Tuple
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from adaptutils.githubutils import GitHubApp
from detection_engine.model import GitHubPRAnalysisOutput, AffectedEndpoint


class GithubDetectionEngine:
    def __init__(self):
        self.github_app = GitHubApp(auth_token=os.getenv("GITHUB_API_TOKEN"))

    def get_pr_diff_and_base_branch_source(
        self, repo_owner: str, repo_name: str, pr_number: int
    ) -> str:

        # Step 1: Get the PR Object
        pr = self.github_app.get_pr(repo_owner, repo_name, pr_number)

        # Step 2: Get the Base Branch Source
        base_branch_source = self.github_app.get_repo_branch_source(
            repo_owner,
            repo_name,
            pr.base.ref,
            include_extensions=[".go", ".project.json"],
        )
        print(pr.base.ref)
        print(pr.base.sha)
        # Step 3: Get the pull request diff
        diff = self.github_app.get_pr_diff_from_diff_url(pr.diff_url)

        # Step 4: Return the base branch source and diff
        base_branch_source_code = ""
        base_branch_source_code += "=" * 50 + "\n"
        base_branch_source_code += "Base Branch Source\n"
        base_branch_source_code += "=" * 50 + "\n"
        for path, content in base_branch_source.items():
            base_branch_source_code += f"--- {path} ---\n{content}\n"
        base_branch_source_code += "\n\n"

        diff_str = ""
        diff_str += "=" * 50 + "\n"
        diff_str += "PR Diff\n"
        diff_str += "=" * 50 + "\n"
        diff_str += diff
        return base_branch_source_code, diff_str
    
    def validate_data(self, data: str) -> Tuple[bool, str]:
        try:
            self.data = GitHubPRAnalysisOutput.model_validate_json(data)
        except Exception as e:
            return False, f"Validation Error: {e}"
        return True, None
    
    def construct_affected_endpoints_notification(self, affected_endpoint: AffectedEndpoint, change_type: str, pr_no: str):
        mutation = gql("""
            mutation NotifyAffectedEndpoints($url: String!, $method: String!, $changeType: String!,
                                            $description: String!, $reason: String!, $originUniqueID: String!) {
                notifyAffectedEndpoints(
                    url: $url
                    method: $method
                    changeType: $changeType
                    description: $description
                    reason: $reason
                    changeOrigin: "githubpr"
                    originUniqueID: $originUniqueID
                ) {
                    id
                }
            }
        """)

        # Define variables for the mutation
        variables = {
            "url": affected_endpoint.endpoint,
            "method": affected_endpoint.methods.method,
            "changeType": change_type,
            "description": affected_endpoint.description,
            "reason": str(affected_endpoint.reasoning),
            "originUniqueID": str(pr_no)
        }
        return mutation, variables
    
    def notify(self, data: str):
        ok, error = self.validate_data(data)
        if not ok:
            return ok, error
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        print(f"URL: {url}")
        # Setup transport for the client
        transport = RequestsHTTPTransport(url=url, verify=False)
        # Create the GraphQL client
        client = Client(transport=transport, fetch_schema_from_transport=True)
        for changes in self.data.analysis_summary.breaking_changes:
            for affected_endpoint in changes.affected_endpoint:
                mutation, variables = self.construct_affected_endpoints_notification(affected_endpoint, "breaking", self.data.pr_id)
                response = client.execute(mutation, variable_values=variables)
                print(f"Breaking Changes Response for endpoint {affected_endpoint.endpoint} and method {affected_endpoint.methods.method} \n Response : {response}")
            
        for changes in self.data.analysis_summary.non_breaking_changes:
            for affected_endpoint in changes.affected_endpoint:
                mutation, variables = self.construct_affected_endpoints_notification(affected_endpoint, "nonbreaking", self.data.pr_id)
                response = client.execute(mutation, variable_values=variables)
                print(f"Non Breaking Changes Response for endpoint {affected_endpoint.endpoint} and method {affected_endpoint.methods.method} \n Response : {response}")
        return True, None