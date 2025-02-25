from typing import Tuple
import json
from crewai import Crew, Agent, Task
from propagation_engine.github.templates import propagate_system_prompt
from propagation_engine.github.engine import GithubPropagationEngine
from propagation_engine.model import GithubPRCodeGenerationOutput, InputAffectedClient, InputGithubProject


class GithubPropagationCrew:
    def __init__(self):
        self.github_propagation_agent: Agent = self.get_github_propagation_agent()
        self.github_propagation_task: Task = self.get_github_propagation_task()
        self.github_propagation_crew: Crew = self.get_github_propagation_crew()

    def get_github_propagation_agent(self) -> Agent:
        return Agent(
            role="API Change Analyzer and Automated Code Fixer",
            goal="The objective of this agent is to precisely analyze breaking changes in a service API and accurately generate the required client-side code modifications. By comparing the API specifications before and after the change, the agent identifies impacted areas in the client codebase and produces a raw Git diff string that directly fixes the breaking change. The generated diff is structured for seamless application as a patch, ensuring correctness, compatibility, and minimal manual intervention. This enables an automated workflow where the changes are pushed to a feature branch and a pull request is created for review.",
            backstory=str(propagate_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_github_propagation_task(self) -> Task:
        return Task(
            description=str(
                propagate_system_prompt["system_prompt"]["instructions"]["steps"]
            )
            + "\nThe Below are the Service Side Changes: {server_side_changes}\n."
            + "\nThe Below are the Client Side Source Code:\n{source_code}\n\n ",
            # expected_output="Generate the JSON output as per the below JSON output Schema using the generated information.\njson outout Schema:{output_schema}\n\n The sample diff string: {sample_diff_string}",
            expected_output="Generate the JSON output as per the below JSON output Schema using the generated information.\njson outout Schema:{output_schema}\n\n",
            output_file="output.json",
            output_json=GithubPRCodeGenerationOutput,
            verbose=True,
            agent=self.github_propagation_agent,
        )

    def get_github_propagation_crew(self) -> Crew:
        return Crew(
            agents=[self.github_propagation_agent],
            tasks=[self.github_propagation_task],
            verbose=True,
        )

    def propagate(self) -> Tuple[bool, str]:
        pe = GithubPropagationEngine()
        # Step 1: Get Action Items for Github PR
        self.action_items = pe.get_action_items()
        if not self.action_items:
            return True, "No Action Item Found...!"
        # [print(data.model_dump_json(indent=4)) for data in self.action_items]

        # Step 2: Process Action Items
        for action_item in self.action_items:
            # Step 2.1: Prepare the Client Source Code
            repo_owner, repo_name = action_item.affectedClient.githubProject.repository.split("/")
            client_source_code = pe.get_client_source_code(repo_owner, repo_name, action_item.affectedClient.githubProject.branch)
            service_side_changes = pe.get_service_side_changes(action_item)
            diff_string : str = ""
            with open("./propagation_engine/github/sample_diff.diff", "r") as file:
                diff_string = file.read()
            inputs = {
                "server_side_changes": service_side_changes,
                "source_code": client_source_code,
                "output_schema": json.dumps(propagate_system_prompt["system_prompt"]["instructions"]["output_schema"]),
                # "sample_diff_string": diff_string
            }

        print(inputs)
        results = self.github_propagation_crew.kickoff(inputs=inputs)
        print(results.json)

        ok, pr_number, pr_url = pe.apply_diff_and_raise_pr(owner=repo_owner, repository= repo_name, base_branch= action_item.affectedClient.githubProject.branch, data= results.json)
        if not ok:
            return False, "Failed"
        
        # Update the Propagation Status, Meta Data and comments in the Action Items Table
        affected_client = InputAffectedClient(jiraProject=InputGithubProject(prId=pr_number, prUrl=pr_url))
        id = pe.update_action_items(id=action_item.id, comments=None, affected_client=affected_client, propagationStatus='inprogress')
        if id != action_item.id:
            return False, "Failed to update the Action Items with Meta Data"
        return True, "Success"
        
