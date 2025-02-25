from typing import List
import time
import json

from crewai import Crew, Agent, Task
from .agent_output_model import OnboardingDataModel, ProjectDataModel, SpecExtractionOutput, Specification
from central_system.templates import extract_onboarding_informations, extratction_system_prompt
from .onboarding_handler import OnboardingHandler
from central_system.database import SessionLocal
from central_system.database.onboarding import Repository, RepoBranch, Status

from adaptutils import get_branch_source_dump


class OnboardingCrew:
    def __init__(self):
        self.source_code_analyzer_agent: Agent = self.get_source_code_analyzer_agent()
        self.source_code_analysis_task: Task = self.get_source_code_analysis_task()
        self.onboarding_crew: Crew = self.get_onboarding_crew()

        self.endpoint_specification_extractor_agent: Agent = self.get_endpoint_specification_extractor_agent()
        self.endpoint_specification_extraction_task: Task = self.get_endpoint_specification_extraction_task()
        self.extraction_crew: Crew = self.get_extraction_crew()

    def get_source_code_analyzer_agent(self) -> Agent:
        return Agent(
            role="Source Code Analyzer",
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
        onboarding_results = self.onboarding_crew.kickoff(inputs=inputs)

        # Step 2.3: Validate the Agent output and Onboard the Repository
        meta_data = ProjectDataModel(repository_url=repository, branch_name=branch)
        handler = OnboardingHandler(meta_data)

        ok, error = handler.validate_onboarding_data(onboarding_results.json)
        if not ok:
            print(error)
            return ok, error
    
        extraction_inputs = {
            "source_code": source_code,
            "example_output": json.dumps(extratction_system_prompt["system_prompt"]["instructions"]["example_output"]),
        }
        specifications: List[Specification] = []
        for endpoint in handler.onboarding_data.exposed_endpoints:
            for method in endpoint.methods:
                extraction_inputs["endpoints_list"] = str([{"endpoint":endpoint.endpoint, "method": method.method}])
                results = self.extraction_crew.kickoff(inputs=extraction_inputs)
                specifications.extend(SpecExtractionOutput.model_validate_json(results.json).endpoints)

        data = handler.onboarding_data.add_specifications(specifications)

        ok, error = handler.onboard(data)
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
                        .filter(RepoBranch.status == Status.PENDING)
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
                            onboarding_results = self.onboarding_crew.kickoff(inputs=inputs)
                            print(f"Onboarding Crew Completed...!")

                            # Step 2.3: Validate the Agent output and Onboard the Repository
                            meta_data = ProjectDataModel(
                                repository_url=repository.url,
                                branch_name=repo_branch.branch,
                            )
                            handler = OnboardingHandler(meta_data)
                            
                            # Step 2.4: Validate Onboarding Crew Response
                            ok, error = handler.validate_onboarding_data(onboarding_results.json)
                            if not ok:
                                print(error)
                                return ok, error
                            
                            # Step 2.5: Extract the API Endpoint Specifications for exposed endpoints
                            extraction_inputs = {
                                "source_code": source_code,
                                "example_output": json.dumps(extratction_system_prompt["system_prompt"]["instructions"]["example_output"]),
                            }
                            specifications: List[Specification] = []
                            for endpoint in handler.onboarding_data.exposed_endpoints:
                                # if endpoint.endpoint.find("swagger") != -1:
                                #     continue
                                for method in endpoint.methods:
                                    # if method.method.find("DELETE") != -1:
                                    extraction_inputs["endpoints_list"] = str([{"endpoint":endpoint.endpoint, "method": method.method}])
                                    print(f"Extracting Specification For Endpoint {endpoint.endpoint} and Method: {method.method}")
                                    results = self.extraction_crew.kickoff(inputs=extraction_inputs)
                                    print(f"Extraction Complete. Results : {results}")
                                    specifications.extend(SpecExtractionOutput.model_validate_json(results.json).endpoints)
                                    print(f"Validation Complete For Endpoint {endpoint.endpoint} and Method: {method.method}")

                            print("Extraction Loop Complete...!")
                            data = handler.onboarding_data.add_specifications(specifications)
                            print("Extracted the Onboarding Data with Specification....")
                            # Step 2.6: Onboard the Server endpoints and other data with specifications into the database.
                            ok, error = handler.onboard(data)
                            if not ok:
                                print(error)
                                repo_branch.status = Status.FAILED
                                db.commit()
                                continue

                            print(
                                f"Onboarding Repo: {repository.url} Branch: {repo_branch.branch} successful."
                            )
                            repo_branch.status = Status.COMPLETED
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
            onboarding_results = self.onboarding_crew.kickoff(inputs=inputs)

            # Step 2.3: Validate the Agent output and Onboard the Repository
            meta_data = ProjectDataModel(
                repository_url=repo_data["repository"], branch_name=repo_data["branch"]
            )
            handler = OnboardingHandler(meta_data)

            # Step 2.4: Validate Onboarding Crew Response
            ok, error = handler.validate_onboarding_data(onboarding_results.json)
            if not ok:
                print(error)
                return ok, error
            
            # Step 2.5: Extract the API Endpoint Specifications for exposed endpoints
            extraction_inputs = {
                "source_code": source_code,
                "example_output": json.dumps(extratction_system_prompt["system_prompt"]["instructions"]["example_output"]),
            }
            specifications: List[Specification] = []
            for endpoint in handler.onboarding_data.exposed_endpoints:
                for method in endpoint.methods:
                    extraction_inputs["endpoints_list"] = str([{"endpoint":endpoint.endpoint, "method": method.method}])
                    results = self.extraction_crew.kickoff(inputs=extraction_inputs)
                    specifications.extend(SpecExtractionOutput.model_validate_json(results.json).endpoints)

            data = handler.onboarding_data.add_specifications(specifications)


            ok, error = handler.onboard(data)
            if not ok:
                print(error)
                return ok, error

            print(
                f"Onboarding Repo: {repo_data['repository']} Branch: {repo_data['branch']} successful."
            )
        return "Success"
