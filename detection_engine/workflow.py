from typing import List
import time

from crewai import Crew, Agent, Task

# from .agent_output_model import OnboardingDataModel, ProjectDataModel
from central_system.templates import extract_onboarding_informations

# from .onboarding_handler import OnboardingHandler
from central_system.database import SessionLocal
from central_system.database.onboarding import Repository, RepoBranch, OnboardingStatus

from adaptutils import get_branch_source_dump


class DetectionCrew:
    def __init__(self):
        self.source_code_analyzer_agent: Agent = self.get_source_code_analyzer_agent()
        self.source_code_analysis_task: Task = self.get_source_code_analysis_task()
        self.onboarding_crew: Crew = self.get_onboarding_crew()

    def get_pr_reviewer_agent(self) -> Agent:
        return Agent(
            role="",
            goal="Analyze the provided source code and extract the requested details as mentioned in the 'instructions' and generate the json output as exactly mentioned in the example json output.",
            backstory="You are an intelligent assistant tasked to analyse and extract important details and dependencies of server/client in a larger solution. You always be correct and accurate in analysing and extracting requested informations. you are abosolutely a professional in generating ready to use json output based on the extracted information and provided expected json sample output.",
            verbose=True,
        )

    def get_source_code_analysis_task(self) -> Task:
        return Task(
            description="instructions:\nGenerate only the JSON Output exactly same as example_json_output. Do not include any other text or comments in the output.,\nExtract the Exposed endpoints and capture them to the JSON Output.,\nExtract the consumed endpoints and capture them to the JSON Output.,\nExtract the bringup configurations such as port number, tls protocol, etc., and capture them to the JSON Output.\nsource:{source}\n example_json_output: {example_json_output}",
            expected_output="Generate the JSON output as per the below JSON example json output using the extract information.\nexample json outout:{example_json_output}",
            output_file="output.json",
            output_json=OnboardingDataModel,
            verbose=True,
            agent=self.source_code_analyzer_agent,
        )

    def get_onboarding_crew(self) -> Crew:
        return Crew(
            agents=[self.source_code_analyzer_agent],
            tasks=[self.source_code_analysis_task],
            verbose=True,
        )

    def onboard(
        self, repository: str, branch: str, included_extensions: List[str]
    ) -> str:
        source_code = get_branch_source_dump(
            repo=repository,
            branch=branch,
            included_extensions=included_extensions,
        )
        example_output = extract_onboarding_informations["example_json_output"]
        inputs = {"source": source_code, "example_json_output": example_output}

        # Step 2.2: Run the Crew and get the Final output
        results = self.onboarding_crew.kickoff(inputs=inputs)

        # Step 2.3: Validate the Agent output and Onboard the Repository
        meta_data = ProjectDataModel(repository_url=repository, branch_name=branch)
        handler = OnboardingHandler(meta_data)

        ok, error = handler.onboard(results.json)
        if not ok:
            print(error)
            return ok, error

        print(f"Onboarding Repo: {repository} Branch: {branch} successful.")
        return True, "Success"

    def run_demon(self) -> str:
        while True:
            time.sleep(1)
            with SessionLocal() as db:
                try:
                    result = (
                        db.query(Repository)
                        .join(RepoBranch)
                        .filter(RepoBranch.status == OnboardingStatus.PENDING)
                        .all()
                    )
                    for repository in result:
                        for repo_branch in repository.repo_branches:
                            # Step 2.1: Retreive Source Code from the Repository and Prepare Agent inputs
                            source_code = get_branch_source_dump(
                                repo=repository.url,
                                branch=repo_branch.branch,
                                included_extensions=repo_branch.included_extensions,
                            )
                            example_output = extract_onboarding_informations[
                                "example_json_output"
                            ]
                            inputs = {
                                "source": source_code,
                                "example_json_output": example_output,
                            }

                            # Step 2.2: Run the Crew and get the Final output
                            results = self.onboarding_crew.kickoff(inputs=inputs)

                            # Step 2.3: Validate the Agent output and Onboard the Repository
                            meta_data = ProjectDataModel(
                                repository_url=repository.url,
                                branch_name=repo_branch.branch,
                            )
                            handler = OnboardingHandler(meta_data)

                            ok, error = handler.onboard(results.json)
                            if not ok:
                                print(error)
                                repo_branch.status = OnboardingStatus.FAILED
                                db.commit()
                                continue

                            print(
                                f"Onboarding Repo: {repository.url} Branch: {repo_branch.branch} successful."
                            )
                            repo_branch.status = OnboardingStatus.COMPLETED
                            db.commit()
                except Exception as e:
                    print(e)
                    db.rollback()
                    continue
                finally:
                    db.close()

    def run(self) -> str:
        # Step 1: Define/Get the repository details
        repository_details = [
            {
                "repository": "sms2sakthivel/user-manager",
                "branch": "master",
                "included_extensions": [".go", ".project.json"],
            },
            {
                "repository": "sms2sakthivel/product-manager",
                "branch": "master",
                "included_extensions": [".go", ".project.json"],
            },
            {
                "repository": "sms2sakthivel/order-manager",
                "branch": "master",
                "included_extensions": [".go", ".project.json"],
            },
            {
                "repository": "sms2sakthivel/payment-manager",
                "branch": "master",
                "included_extensions": [".go", ".project.json"],
            },
        ]
        # Step 2: Iterate through the repositories and onboard one by one.
        for repo_data in repository_details:
            # Step 2.1: Retreive Source Code from the Repository and Prepare Agent inputs
            source_code = get_branch_source_dump(
                repo=repo_data["repository"],
                branch=repo_data["branch"],
                included_extensions=repo_data["included_extensions"],
            )
            example_output = extract_onboarding_informations["example_json_output"]
            inputs = {"source": source_code, "example_json_output": example_output}

            # Step 2.2: Run the Crew and get the Final output
            results = self.onboarding_crew.kickoff(inputs=inputs)

            # Step 2.3: Validate the Agent output and Onboard the Repository
            meta_data = ProjectDataModel(
                repository_url=repo_data["repository"], branch_name=repo_data["branch"]
            )
            handler = OnboardingHandler(meta_data)

            ok, error = handler.onboard(results.json)
            if not ok:
                print(error)
                return ok, error

            print(
                f"Onboarding Repo: {repo_data['repository']} Branch: {repo_data['branch']} successful."
            )
        return "Success"
