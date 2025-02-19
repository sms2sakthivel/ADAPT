import os
from typing import Tuple
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests
import json

from detection_engine.model import JIRATicketExtractionOutput, JIRATicketAnalysisOutput, AffectedEndpoint


class JIRADetectionEngine:
    def __init__(self):
        self.jira_user_pat = os.environ["JIRA_USER_PAT"]


    def download_file_as_string(self, url: str) -> str:
        url = url.replace("http://localhost", "http://host.docker.internal")
        headers = {
            "Authorization": f"Bearer {self.jira_user_pat}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure we catch HTTP errors
        return response.text  # Use .text for text files, .content for binary

    def extract_jira_data(self, data: dict) -> Tuple[str, dict]:
        jira_data = {
            "ticket" :{
                "id": data["issue"]["id"],
                "url": data["issue"]["self"],
                "type": data["issue"]["fields"]["issuetype"]["name"],
            },
            "project": {
                "name": data["issue"]["fields"]["project"]["name"]
            },
            "priority": data["issue"]["fields"]["priority"]["name"],
            "status": data["issue"]["fields"]["status"]["name"],
            "description": data["issue"]["fields"]["description"],
            "comments": data["issue"]["fields"]["comment"]["comments"],
            "attachements": [],
        }
        for attachement in data["issue"]["fields"]["attachment"]:
            if str(attachement["filename"]).split('.')[1].lower() in ["yaml", "json", "yml"]:
                jira_data["attachements"].append({
                    "filename": attachement["filename"],
                    "content": self.download_file_as_string(attachement["content"])
                })
        return json.dumps(jira_data), jira_data



    def construct_endpoint_query(self, url: str, method: str):
        query = gql("""
            query GetEndpointDetails($url: String!, $method: String!) {
                endpoint(url: $url, method: $method) {
                    id
                    url
                    method
                    description
                    specification
                }
            }
        """)

        # Define variables for the query
        variables = {
            "url": url,
            "method": method
        }

        return query, variables

    def validate_extracted_data(self, data: str) -> Tuple[bool, str]:
        try:
            self.extraction_data = JIRATicketExtractionOutput.model_validate_json(data)
        except Exception as e:
            return False, f"Validation Error: {e}"
        return True, None

    def validate_analysis_data(self, data: str) -> Tuple[bool, str]:
        try:
            self.analysis_data = JIRATicketAnalysisOutput.model_validate_json(data)
        except Exception as e:
            return False, f"Validation Error: {e}"
        return True, None

    def construct_affected_endpoints_notification(self, affected_endpoint: AffectedEndpoint, change_type: str, jira_ticket_id: str):
        mutation = gql("""
            mutation NotifyAffectedEndpoints($url: String!, $method: String!, $changeType: String!,
                                            $description: String!, $reason: String!, $originUniqueID: String!) {
                notifyAffectedEndpoints(
                    url: $url
                    method: $method
                    changeType: $changeType
                    description: $description
                    reason: $reason
                    changeOrigin: "jiraticket"
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
            "originUniqueID": str(jira_ticket_id)
        }
        return mutation, variables
    

    def get_endpoint_specifications(self, data: str) -> dict:
        ok, _ = self.validate_extracted_data(data)
        if not ok:
            return None
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        # print(f"URL: {url}")
        # Setup transport for the client
        transport = RequestsHTTPTransport(url=url, verify=False)
        # Create the GraphQL client
        client = Client(transport=transport, fetch_schema_from_transport=True)
        existing_specification = {}
        for endpoint in self.extraction_data.identified_endpoints:
            query, variables = self.construct_endpoint_query(url=endpoint.endpoint,method=endpoint.methods.method)
            response = client.execute(query, variable_values=variables)
            if response['endpoint']:
                print(f"Specification Identified for endpiont {endpoint} and method {endpoint.methods.method}")
                if endpoint.endpoint not in existing_specification:
                    existing_specification[endpoint.endpoint] = []
                existing_specification[endpoint.endpoint].extend(response['endpoint'])
            else:
                print(f"Specification not found for endpiont {endpoint} and method {endpoint.methods.method}")
        return existing_specification

    def notify(self, data: str):
        ok, error = self.validate_analysis_data(data)
        if not ok:
            return ok, error
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        print(f"URL: {url}")
        # Setup transport for the client
        transport = RequestsHTTPTransport(url=url, verify=False)
        # Create the GraphQL client
        client = Client(transport=transport, fetch_schema_from_transport=True)
        for changes in self.analysis_data.analysis_summary.breaking_changes:
            for affected_endpoint in changes.affected_endpoint:
                mutation, variables = self.construct_affected_endpoints_notification(affected_endpoint, "breaking", self.analysis_data.ticket_id)
                response = client.execute(mutation, variable_values=variables)
                print(f"Breaking Changes Response for endpoint {affected_endpoint.endpoint} and method {affected_endpoint.methods.method} \n Response : {response}")
            
        for changes in self.analysis_data.analysis_summary.non_breaking_changes:
            for affected_endpoint in changes.affected_endpoint:
                mutation, variables = self.construct_affected_endpoints_notification(affected_endpoint, "nonbreaking", self.analysis_data.ticket_id)
                response = client.execute(mutation, variable_values=variables)
                print(f"Non Breaking Changes Response for endpoint {affected_endpoint.endpoint} and method {affected_endpoint.methods.method} \n Response : {response}")
        return True, None