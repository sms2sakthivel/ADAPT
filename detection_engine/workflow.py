import json
from crewai import Crew, Agent, Task
from detection_engine.templates import detection_system_prompt
from detection_engine.model import GitHubPRAnalysisOutput
from detection_engine.detection_engine import DetectionEngine


class DetectionCrew:
    def __init__(self):
        self.pr_reviewer_agent: Agent = self.get_pr_reviewer_agent()
        self.pr_review_task: Task = self.get_pr_review_task()
        self.detection_crew: Crew = self.get_detection_crew()

    def get_pr_reviewer_agent(self) -> Agent:
        return Agent(
            role="Github PR Reviewer and Interface Change Detector and Classifier",
            goal="The objective of this GitHub PR Reviewer Agent is to systematically analyze and compare the differences between a Pull Request (PR) Diff and the base branch code to identify and classify changes in API interface specifications. The agent will classify these changes as either Breaking or Non-Breaking based on a predefined set of criteria, and provide a structured JSON output with detailed reasoning for each classification, ensuring compatibility across various languages and frameworks.",
            backstory=str(detection_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_pr_review_task(self) -> Task:
        return Task(
            description=str(
                detection_system_prompt["system_prompt"]["instructions"]["steps"]
            )
            + "\nThe PR DIFF is as follows:\n{pr_diff} and the Base Branch Source Code is as follows:\n{base_source_code} and the PR ID is {pr_id}",
            expected_output="Generate the JSON output as per the below JSON output Schema using the extracted information.\njson outout Schema:{output_schema}",
            output_file="output.json",
            output_json=GitHubPRAnalysisOutput,
            verbose=True,
            agent=self.pr_reviewer_agent,
        )

    def get_detection_crew(self) -> Crew:
        return Crew(
            agents=[self.pr_reviewer_agent],
            tasks=[self.pr_review_task],
            verbose=True,
        )

    def detect(self, repo_owner: str, repo_name: str, pr_number: int) -> str:
        de = DetectionEngine()
        pr_diff, base_source_code = de.detect_pr_interface_changes(
            repo_owner, repo_name, pr_number
        )
        inputs = {
            "pr_id": str(pr_number),
            "pr_diff": pr_diff,
            "base_source_code": base_source_code,
            "output_schema": json.dumps(
                detection_system_prompt["system_prompt"]["instructions"][
                    "output_schema"
                ]
            ),
        }

        # Step 2.2: Run the Crew and get the Final output
        results = self.detection_crew.kickoff(inputs=inputs)
        print(results.json)

        # Step 2.3: Validate the Agent output and Onboard the Repository
        # meta_data = ProjectDataModel(repository_url=repository, branch_name=branch)
        # handler = OnboardingHandler(meta_data)

        # ok, error = handler.onboard(results.json)
        # if not ok:
        #     print(error)
        #     return ok, error

        print(
            f"Completed Detection Task For: {repo_owner}/{repo_name} PR: {pr_number} successful."
        )
        return True, "Success"
