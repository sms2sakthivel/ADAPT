from typing import Tuple
import json
from crewai import Agent, Task, Crew
from propagation_engine.jira.template import propagation_system_prompt
from propagation_engine.jira.engine import JiraPropagationEngine
from propagation_engine.model import JiraTicketGenerationOutput, InputAffectedClient, InputJiraProject

class JiraPropagationCrew:
    def __init__(self):
        self.jira_propagation_agent: Agent = self.get_jira_propagation_agent()
        self.jira_propagation_task: Task = self.get_jira_propagation_task()

        self.jira_propagation_crew: Crew = self.get_jira_propagation_crew()


    def get_jira_propagation_agent(self) -> Agent:
        return Agent(
            role=propagation_system_prompt["system_prompt"]["role"],
            goal=propagation_system_prompt["system_prompt"]["goal"],
            backstory=str(propagation_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_jira_propagation_task(self) -> Task:
        return Task(
            description=str(propagation_system_prompt["system_prompt"]["instructions"]["steps"])
            + "\nThe Below are the Service Side Changes: {server_side_changes}\n.",
            # expected_output="Generate the JSON output as per the below JSON output Schema using the generated information.\njson outout Schema:{output_schema}\n\n The sample diff string: {sample_diff_string}",
            expected_output="Generate the JSON output as per the below JSON output Schema using the generated information.\njson outout Schema:{output_schema}\n\n",
            output_file="output.json",
            output_json=JiraTicketGenerationOutput,
            verbose=True,
            agent=self.jira_propagation_agent,
        )

    def get_jira_propagation_crew(self) -> Crew:
        return Crew(
            agents=[self.jira_propagation_agent],
            tasks=[self.jira_propagation_task],
            verbose=True,
        )

    def propagate(self) -> Tuple[bool, str]:
        pe = JiraPropagationEngine()
        # Step 1: Get Action Items for Github PR
        self.action_items = pe.get_action_items()
        if not self.action_items:
            return True, "No Action Item Found...!"
        # [print(data.model_dump_json(indent=4)) for data in self.action_items]

        # Step 2: Process Action Items
        for action_item in self.action_items:
            service_side_changes = pe.get_service_side_changes(action_item)
            inputs = {
                "server_side_changes": service_side_changes,
                "output_schema": json.dumps(propagation_system_prompt["system_prompt"]["instructions"]["output_schema"]),
                # "sample_diff_string": diff_string
            }

            print(inputs)
            results = self.jira_propagation_crew.kickoff(inputs=inputs)
            # print(results.json)
            jira_output = results.json_dict
            # jira_output = {"title": "Breaking Change: User Management Service - Update GET /users/{id} Response Structure", "summary": "The response structure of the GET /users/{id} endpoint has changed, requiring updates to client implementations.", "description": "The user_name and user_id attributes have been removed from the response object for the /users/{id} endpoint to enhance user privacy and data integrity. This change is necessary to comply with privacy regulations, and impacts all clients using this endpoint. Clients must adapt their response handling logic to align with this update.", "issue_type": "Bug", "priority": "High", "severity": "Critical", "affected_endpoint": "/users/{id}", "impact": "Clients relying on the user_name and user_id fields in the response will need to update their implementations to handle the removal of these attributes. Missing fields may cause errors or unexpected behavior in the client applications.", "required_changes": "Clients must update their code to remove references to user_name and user_id in the response parsing logic from the GET /users/{id} API. Ensure to account for only the non-sensitive fields: email and name available in the updated response.", "definition_of_ready": "Client teams have reviewed the impact of the change and identified necessary updates to client-side code. Required tests are outlined and planned.", "definition_of_done": "Client implementations have been updated to successfully retrieve and process the revised response structure. All related unit and integration tests have been executed and passed.", "references": [{"title": "Service Change Ticket", "url": "http://localhost:8080/rest/api/2/issue/10100"}]}

            jira_ticket_data = JiraTicketGenerationOutput.model_validate(jira_output)
            ticket_id, ticket_url = pe.raise_jira_ticket(action_item=action_item, ticket_data=jira_ticket_data)
            affected_client = InputAffectedClient(jiraProject=InputJiraProject(ticketId=ticket_id, ticketUrl=ticket_url))
            id = pe.update_action_items(id=action_item.id, comments=None, affected_client=affected_client, propagationStatus='inprogress')
            if id != action_item.id:
                return False, "Failed to update the Action Items with Meta Data"

        return True, "Success"