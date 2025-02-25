from typing import List
import json
from crewai import Crew, Agent, Task
from detection_engine.templates import detection_system_prompt,  extratction_system_prompt
from detection_engine.model import GitHubPRAnalysisOutput, SpecExtractionOutput, Specification, GitHubPRAnalysisOutputWithSpecification
from detection_engine.github.engine import GithubDetectionEngine


class GithubDetectionCrew:
    def __init__(self):
        self.pr_reviewer_agent: Agent = self.get_pr_reviewer_agent()
        self.pr_review_task: Task = self.get_pr_review_task()
        self.detection_crew: Crew = self.get_detection_crew()

        self.endpoint_specification_extractor_agent: Agent = self.get_endpoint_specification_extractor_agent()
        self.endpoint_specification_extraction_task: Task = self.get_endpoint_specification_extraction_task()
        self.extraction_crew: Crew = self.get_extraction_crew()

    def get_pr_reviewer_agent(self) -> Agent:
        return Agent(
            role="Github PR Reviewer and Interface Change Detector and Classifier",
            goal="The objective of this GitHub PR Reviewer Agent is to systematically analyze and compare the differences between a Pull Request (PR) Diff and the base branch code to identify and classify changes in API interface specifications. The agent will classify these changes as either Breaking or Non-Breaking based on a predefined set of criteria, and provide a structured JSON output with detailed reasoning for each classification, ensuring compatibility across various languages and frameworks.",
            backstory=str(detection_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_pr_review_task(self) -> Task:
        return Task(
            description="Instructions :\n Steps:\n" + str(
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

    def get_endpoint_specification_extractor_agent(self) -> Agent:
        return Agent(
            role="API Specification Extraction Agent",
            goal="To analyze the provided source code and extract a comprehensive, structured API endpoint specification, ensuring accuracy, completeness, and adherence to API documentation standards. The agent must detect and extract all relevant attributes of each endpoint, including methods, paths, parameters, request/response schemas, authentication, and constraints, while handling framework-specific variations.",
            backstory=str(extratction_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_endpoint_specification_extraction_task(self) -> Task:
        return Task(
            description="Instructions :\n Steps:\n" + str(
                extratction_system_prompt["system_prompt"]["instructions"]["steps"]
            )
            + "\nThe Github Source Code is as follows:\n{source_code}. The list of endpoint specifications to be extracted are {endpoints_list}",
            expected_output="Generate the JSON output using the extracted information.\nExample json outout :{example_output}",
            output_json=SpecExtractionOutput,
            verbose=True,
            agent=self.endpoint_specification_extractor_agent,
        )

    def get_extraction_crew(self) -> Crew:
        return Crew(
            agents=[self.endpoint_specification_extractor_agent],
            tasks=[self.endpoint_specification_extraction_task],
            verbose=True,
        )


    def detect(self, repo_owner: str, repo_name: str, pr_number: int, pr_url: str) -> str:
        de = GithubDetectionEngine()
        base_source_code, pr_diff = de.get_pr_diff_and_base_branch_source(
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
            )
        }

        print(inputs)

        # Step 2.2: Run the Crew and get the Final output
        detection_results = self.detection_crew.kickoff(inputs=inputs)

        ok, error = de.validate_detection_data(detection_results.json)
        if not ok:
            print(error)
            return ok, error

        source_code = de.get_feature_branch_source(repo_owner, repo_name, pr_number)
        extraction_inputs = {
            "source_code": source_code,
            "example_output": json.dumps(extratction_system_prompt["system_prompt"]["instructions"]["example_output"]),
        }
        specifications: List[Specification] = []
        for change in de.detection_data.analysis_summary.breaking_changes:
            for endpoint in change.affected_endpoint:
                extraction_inputs["endpoints_list"] = str([{"endpoint":endpoint.endpoint, "method": endpoint.methods.method}])
                results = self.extraction_crew.kickoff(inputs=extraction_inputs)
                specifications.extend(SpecExtractionOutput.model_validate_json(results.json).endpoints)

        for change in de.detection_data.analysis_summary.non_breaking_changes:
            for endpoint in change.affected_endpoint:
                extraction_inputs["endpoints_list"] = str([{"endpoint":endpoint.endpoint, "method": endpoint.methods.method}])
                results = self.extraction_crew.kickoff(inputs=extraction_inputs)
                specifications.extend(SpecExtractionOutput.model_validate_json(results.json).endpoints)
        

        data = de.detection_data.add_specifications(str(pr_number), specifications)
        ok, error = de.notify(data, pr_url)
        if not ok:
            print(error)
            return ok, error

        print(
            f"Completed Detection Task For: {repo_owner}/{repo_name} PR: {pr_number} successful."
        )
        return True, "Success"
