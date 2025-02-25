import os
from typing import List, Tuple
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from adaptutils.githubutils import GitHubApp
from propagation_engine.model import ActionItemsResponse, ActionItem, GithubPRCodeGenerationOutput, InputAffectedClient


class GithubPropagationEngine:
    def __init__(self):
        self.github_app = GitHubApp(auth_token=os.getenv("GITHUB_API_TOKEN"))

    def get_action_items(self) -> List[ActionItem]:
        # Step 1: Setup GraphQL Client Object
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        transport = RequestsHTTPTransport(url=url, verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Step 2: Query the Action Items
        query, variable = self.construct_action_items_query()
        response = client.execute(query, variable_values=variable)
        if response['actionItems']:
            print(f"Identified Action Items for Github PR. Number of Action Items : {len(response['actionItems'])}")
            return ActionItemsResponse.model_validate(response).actionItems
        else:
            print(f"No Action Item Identified for Github PR")
        return None

    def construct_action_items_query(self):
        query = gql(
            """
            query GetEndpointDetails($type: String!, $propagationStatus: String!) {
                actionItems(type: $type, propagationStatus: $propagationStatus){
                    id
                    type
                    comments
                    propagationStatus
                    originatingService{
                    name
                    guid
                    githubProject{
                        repository
                        branch
                        prId
                        prUrl
                    }
                    jiraProject{
                        url
                        id
                        ticketId
                        ticketUrl
                    }
                    affectedEndpoint{
                        id
                        url
                        method
                        changeType
                        description
                        reason
                        changeOrigin
                        originUniqueID
                        changeOriginURL
                        status
                        currentSpecification
                        specificationAfterTheChange
                    }
                    }
                    affectedClient{
                    name
                    guid
                    githubProject{
                        repository
                        branch
                        prId
                        prUrl
                    }
                    jiraProject{
                        url
                        id
                        ticketId
                        ticketUrl
                    }
                    }
                }                    
            }
        """
        )
        # Define variables for the query
        variables = {
            "type": "githubpr",
            "propagationStatus": "pending",
        }
        return query, variables

    def get_client_source_code(self, repo_owner: str, repo_name: str, branch: str) -> str:
        # Step 1: Get the Branch Source
        source_code_data = self.github_app.get_repo_branch_source(
            repo_owner,
            repo_name,
            branch= branch,
            include_extensions=[".go", ".project.json", ".json", ".yaml", ".yml"],
        )
        
        # Step 2: Return the branch source
        source_code = ""
        source_code += "=" * 50 + "\n"
        source_code += "Client Source Code\n"
        source_code += "=" * 50 + "\n"
        for path, content in source_code_data.items():
            source_code += f"--- {path} ---\n{content}\n"
        source_code += "=" * 50 + "\n\n"

        return source_code

    def get_service_side_changes(self, action_item: ActionItem) -> str:
        # Step 1: Construct Service Side Changes
        service_side_change = ""
        service_side_change += "=" * 50 + "\n"
        service_side_change += "Service Side Changes\n"
        service_side_change += "=" * 50 + "\n"

        # Add Endpoint Data:
        service_side_change += "Endpoint Details : \n"
        service_side_change += "URL : " + action_item.originatingService.affectedEndpoint.url + "\n"
        service_side_change += "Method : " + action_item.originatingService.affectedEndpoint.method + "\n"
        service_side_change += "Description : " + action_item.originatingService.affectedEndpoint.description + "\n"
        service_side_change += "Why and How is it breaking the Clients : \n" + action_item.originatingService.affectedEndpoint.reason + "\n"
        service_side_change += "Previous Endpoint Specification : \n" + action_item.originatingService.affectedEndpoint.currentSpecification + "\n\n"
        service_side_change += "Updated Endpoint Specification : \n" + action_item.originatingService.affectedEndpoint.specificationAfterTheChange + "\n"
        service_side_change += "=" * 50 + "\n"
        return service_side_change


    def apply_diff_and_raise_pr(self, owner: str, repository: str, base_branch: str, data: str) -> bool:
        ok, _ = self.validate_data(data)
        if not ok:
            return ok
        return self.github_app.apply_diff_and_raise_pr(
            owner= owner,
            repository= repository,
            feature_branch= self.data.branch,
            base_branch= base_branch,
            commit_message= self.data.commit_message,
            diff_str=self.data.diff_string,
            pr_title=self.data.pull_request.title,
            pr_description= self.data.pull_request.description,
        )
    def validate_data(self, data: str) -> Tuple[bool, str]:
        try:
            self.data = GithubPRCodeGenerationOutput.model_validate_json(data)
        except Exception as e:
            return False, f"Validation Error: {e}"
        return True, None


    def construct_update_action_items(self, id: int, comments: str, affected_client: InputAffectedClient, propagationStatus: str):
        mutation = gql("""
            mutation NotifyAffectedEndpoints(id: int!, $comments: String, $affected_client: AffectedClientInput,
                                            $propagationStatus: String) {
                updateActionItem(
                    id: $id
                    comments: $comments
                    affected_client: $affected_client
                    propagationStatus: $propagationStatus
                ) {
                    id
                }
            }
        """)

        # Define variables for the mutation
        variables = {
            "id": id,
            "comments": comments,
            "affected_client": InputAffectedClient.model_dump_json(),
            "propagationStatus": propagationStatus
        }
        return mutation, variables
    

    def update_action_items(self, id: int, comments: str, affected_client: InputAffectedClient, propagationStatus: str) -> int:
        # Step 1: Setup GraphQL Client Object
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        transport = RequestsHTTPTransport(url=url, verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Step 2: Query the Action Items
        query, variable = self.construct_update_action_items(id=id, comments=comments, affected_client=affected_client, propagationStatus=propagationStatus)
        response = client.execute(query, variable_values=variable)
        print(response)
        if response:
            print(f"Action Item is updated with Meta Data")
            return response
        else:
            print(f"No Action Item Identified for Github PR")
        return None