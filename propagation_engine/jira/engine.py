import os
import json
from typing import List
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from jira import JIRA

from propagation_engine.model import ActionItemsResponse, ActionItem, JiraTicketGenerationOutput, InputAffectedClient


class JiraPropagationEngine:
    def __init__(self):
        self.jira_user_pat = os.environ["JIRA_USER_PAT"]

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
            print(f"Identified Action Items for JIRA Ticket. Number of Action Items : {len(response['actionItems'])}")
            return ActionItemsResponse.model_validate(response).actionItems
        else:
            print(f"No Action Item Identified for JIRA Ticket")
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
            "type": "jiraticket",
            "propagationStatus": "pending",
        }
        return query, variables

    def get_service_side_changes(self, action_item: ActionItem) -> str:
        # Step 1: Construct Service Side Changes
        service_side_change = "=" * 50 + "\n" + "Service Name: " + action_item.originatingService.name + "\n"
        service_side_change += "Service Project: " + action_item.originatingService.jiraProject.url + "\n"
        service_side_change += "Reference Jira Ticket: " + action_item.originatingService.jiraProject.ticketUrl + "\n"
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

    def raise_jira_ticket(self, action_item: ActionItem, ticket_data: JiraTicketGenerationOutput):
        """
        Raises a JIRA ticket for the client service based on the breaking change.
        
        :param jira_project_id: The JIRA project key where the ticket should be raised.
        :param ticket_data: Dictionary containing details for the JIRA ticket.
        :return: Created JIRA ticket key and URL.
        """
        # Authenticate using Personal Access Token (PAT)
        jira_options = {"server": os.environ["JIRA_SERVER"]}
        jira = JIRA(jira_options, token_auth=self.jira_user_pat)

        description = f"*{ticket_data.title}*\n\n"
        description += f"{ticket_data.description}\n\n"
        description += f"*Affected Endpoint:* \n\t{ticket_data.affected_endpoint}\n"
        description += f"*Impact:* \n\t{ticket_data.impact}\n"
        description += f"*Required Changes:* \n\t{ticket_data.required_changes}\n"
        description += f"*Definition of Ready:* \n\t{ticket_data.definition_of_ready}\n"
        description += f"*Definition of Done:* \n\t{ticket_data.definition_of_done}\n\n"
        description = description.replace("{", "\\{").replace("}", "\\}")
        # Construct the issue payload
        issue_dict = {
            "project": {"key": action_item.affectedClient.jiraProject.id},
            "summary": ticket_data.summary,
            "description": description,
            "issuetype": {"name": ticket_data.issue_type},
            "priority": {"name": ticket_data.priority},
        }

        # Create the issue
        new_issue = jira.create_issue(fields=issue_dict)
        
        # Step 2: Formally Link the Issue in Jira
        jira.create_issue_link(type="Relates",inwardIssue=new_issue.key,outwardIssue=action_item.originatingService.jiraProject.ticketId)
        print(f"Linked {new_issue.key} to {action_item.affectedClient.jiraProject.ticketId}")

        # Print and return ticket details
        jira_ticket_url = f"{os.environ['JIRA_SERVER']}/browse/{new_issue.key}"
        print(f"JIRA Ticket Created: {new_issue.key} - {jira_ticket_url}")
        return new_issue.key, jira_ticket_url


    def construct_update_action_items(self, id: int, comments: str, affected_client: dict, propagationStatus: str):
        # Ensure affected_client is properly structured
        if affected_client is None:
            affected_client = {"githubProject": None, "jiraProject": None}

        if not isinstance(affected_client, dict):
            raise TypeError("affected_client must be a dictionary")

        # Ensure jiraProject exists
        if "jiraProject" not in affected_client or affected_client["jiraProject"] is None:
            affected_client["jiraProject"] = {"ticketId": None, "ticketUrl": None}

        mutation = gql("""
            mutation NotifyAffectedEndpoints($id: ID!, $comments: String, $affected_client: AffectedClientInput,
                                            $propagationStatus: String) {
                updateActionItem(
                    id: $id
                    comments: $comments
                    affected_client: $affected_client
                    propagationStatus: $propagationStatus
                )
            }
        """)

        # Define variables for the mutation
        variables = {
            "id": id,
            "comments": comments,
            "affected_client": affected_client,
            "propagationStatus": propagationStatus
        }
        print("Mutation Variables:", json.dumps(variables, indent=2))  # Debugging
        return mutation, variables
    

    def update_action_items(self, id: int, comments: str, affected_client: InputAffectedClient, propagationStatus: str) -> int:
        # Step 1: Setup GraphQL Client Object
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        transport = RequestsHTTPTransport(url=url, verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Step 2: Query the Action Items
        query, variable = self.construct_update_action_items(id=id, comments=comments, affected_client=affected_client.model_dump(), propagationStatus=propagationStatus)
        response = client.execute(query, variable_values=variable)
        print(response)
        if 'updateActionItem' in response:
            print(f"Action Item is updated with Meta Data")
            return response['updateActionItem']
        else:
            print(f"No Action Item Identified for JIRA Ticket")
        return None