import json
from crewai import Agent, Task, Crew
from detection_engine.model import JIRATicketExtractionOutput, JIRATicketAnalysisOutput
from detection_engine.jira.template.template import jira_ticket_api_data_extraction_system_prompt, jira_api_change_analyzer_system_prompt
from detection_engine.jira.engine import JIRADetectionEngine

class JIRADetectionCrew:
    def __init__(self):
        self.jira_extractor_agent: Agent = self.get_jira_extractor_agent()
        self.jira_extraction_task: Task = self.get_jira_extraction_task()
        self.api_change_analyzer_agent: Agent = self.get_change_analyzer_agent()
        self.api_change_analysis_task: Task = self.get_change_analysis_task()

        self.extraction_crew: Crew = self.get_extraction_crew()
        self.analysis_crew: Crew = self.get_analysis_crew()


    def get_jira_extractor_agent(self):
        return Agent(
            role="An autonomous assistant specializing in analyzing JIRA tickets to extract and document discussed API endpoints, including their HTTP methods and data schemas.",
            goal="To accurately identify and detail API endpoints referenced within a JIRA ticket, providing structured information on their methods, request/response schemas, and any pertinent notes, thereby facilitating efficient API change management.",
            backstory=str(jira_ticket_api_data_extraction_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_jira_extraction_task(self):
        return Task(
            description=str(
                jira_ticket_api_data_extraction_system_prompt["system_prompt"]["instructions"]["steps"]
            )
            + "\nThe JIRA Ticket Data is as follows:\n{jira_ticket_data}",
            expected_output="Generate the JSON output as per the below JSON output Schema using the extracted information.\njson outout Schema:{output_schema}",
            output_file="api_extraction_output.json",
            output_json= JIRATicketExtractionOutput,
            verbose=True,
            agent=self.jira_extractor_agent,
        )

    def get_change_analyzer_agent(self):
        return Agent(
            role="An autonomous assistant specializing in analyzing JIRA tickets to identify and classify proposed changes in REST API interface specifications, ensuring accurate differentiation between breaking and non-breaking changes",
            goal="To meticulously examine JIRA ticket details, comments, and attachments to detect proposed REST API modifications, classify them appropriately, and determine their approval status, providing a structured JSON report to facilitate informed decision-making",
            backstory=str(jira_api_change_analyzer_system_prompt["system_prompt"]["objective"]),
            verbose=True,
        )

    def get_change_analysis_task(self):
        return Task(
            description=str(
                jira_ticket_api_data_extraction_system_prompt["system_prompt"]["instructions"]["steps"]
            )
            + "\nThe JIRA Ticket Data is as follows:\n{jira_ticket_data}" + "\n The Existing API Specifications are as follows {existing_api_specification}",
            expected_output="Generate the JSON output as per the below JSON output Schema using the extracted information.\njson outout Schema:{output_schema}",
            output_file="api_analysis_output.json",
            output_json= JIRATicketAnalysisOutput,
            verbose=True,
            agent=self.jira_extractor_agent,
        )
    
    def get_extraction_crew(self):
        return Crew(
            agents=[self.jira_extractor_agent],
            tasks=[self.jira_extraction_task],
            verbose=True,
        )

    def get_analysis_crew(self):
        return Crew(
            agents=[self.api_change_analyzer_agent],
            tasks=[self.api_change_analysis_task],
            verbose=True,
        )

    def detect(self, data: dict):
        de = JIRADetectionEngine()
        jira_data, jira_data_dict = de.extract_jira_data(data)
        inputs = {
            "jira_ticket_data": json.dumps(jira_data),
            "output_schema": json.dumps(
                jira_ticket_api_data_extraction_system_prompt["system_prompt"]["instructions"][
                    "output_schema"
                ]
            ),
        }

        # print(inputs)
        # Step 2.2: Run the Crew and get the Final output
        results = self.extraction_crew.kickoff(inputs=inputs)
        # print(results.json)
        existing_specification = de.get_endpoint_specifications(results.json)

        inputs["existing_api_specification"] = existing_specification
        inputs["output_schema"] = json.dumps(jira_api_change_analyzer_system_prompt["system_prompt"]["instructions"]["output_schema"])
        # print("\n\n\n ********** INPUT **************")
        # print(inputs)

        results = self.analysis_crew.kickoff(inputs=inputs)
        # print("\n\n\n ********** OUTPUT **************")
        # print(results.json)
        ok, error = de.notify(results.json)
        if not ok:
            print(error)
            return ok, error

        print(
            f"Completed Detection Task For: {jira_data_dict['project']['name']} Ticket ID: {jira_data_dict['ticket']['id']} successful."
        )
        return True, "Success"

# def fetch_existing_specifications(identified_endpoints: List[EndpointWithSpec]) -> Dict[str, Any]:
#     """
#     Fetch existing API specifications from the database for the given endpoints.
#     """
#     existing_specs = {}
#     for endpoint in identified_endpoints:
#         # Replace with actual database retrieval logic
#         existing_specs[endpoint.endpoint] = {
#             "methods": ["GET", "POST"],  # Example data
#             "request_schema": {"example": "Existing request schema"},
#             "response_schema": {"example": "Existing response schema"}
#         }
#     return existing_specs

# # Agent 1: Extract API details from JIRA ticket
# jira_extraction_agent = Agent(
#     name="JIRA API Extraction Agent",
#     role="An assistant that extracts discussed API endpoints from JIRA tickets.",
#     goal="Identify API endpoints mentioned in a given JIRA ticket.",
#     backstory="An expert in analyzing JIRA tickets to extract relevant API discussions.",
#     allow_delegation=False,
#     verbose=True
# )

# # Agent 2: Compare and analyze API changes
# api_analysis_agent = Agent(
#     name="API Change Analysis Agent",
#     role="An analyst comparing proposed API changes with existing specifications.",
#     goal="Determine the nature of API changes and their approval status. Use the Existing Specifications of the endpoints for comparision. Existing Sepcification : {existing_specification}",
#     backstory="A specialist in assessing API modifications for potential impacts.",
#     allow_delegation=False,
#     verbose=True
# )

# # Callback function to fetch existing specifications
# def fetch_spec_callback(output: TaskOutput) -> ExtractionOutput:
#     existing_specs = fetch_existing_specifications(output.to_dict()["identified_endpoints"])
#     extraction_output_with_specs = output.to_dict()
#     extraction_output_with_specs['existing_specifications'] = existing_specs
#     if output.json_dict:
#         output.json_dict['existing_specifications']= existing_specs
#     elif output.pydantic:
#         output.pydantic.existing_specifications = existing_specs
#     print(extraction_output_with_specs)
#     return ExtractionOutput(**extraction_output_with_specs)

# # Task 1: Extract API endpoints from JIRA ticket
# extract_api_task = Task(
#     description="Analyze the JIRA ticket to extract discussed API endpoints.",
#     expected_output="A structured JSON with identified API endpoints.",
#     agent=jira_extraction_agent,
#     output_pydantic=ExtractionOutput,
# )

# # Task 2: Compare extracted API spec with existing spec
# compare_api_task = Task(
#     description="Compare the extracted API details with existing specifications to identify changes.",
#     expected_output="A JSON report detailing breaking/non-breaking changes and approval status.",
#     agent=api_analysis_agent,
#     output_pydantic=ComparisonOutput
# )

# # Define the crew
# jira_api_review_crew = Crew(
#     agents=[jira_extraction_agent, api_analysis_agent],
#     tasks=[extract_api_task, compare_api_task],
#     verbose=True
# )

# Run the workflow

# Step 1: Run Extraction Task
# extraction_crew = Crew(
#     agents=[jira_extraction_agent],
#     tasks=[extract_api_task],
#     verbose=True
# )

# Run the extraction process
# extraction_result = extraction_crew.kickoff()
# extracted_output = extraction_result.pydantic

# print(extracted_output.model_dump_json(indent=4))

# Step 2: Fetch existing API specifications
# existing_specs = fetch_existing_specifications(extracted_output.identified_endpoints)

# # Step 3: Prepare input for Comparison Task
# comparison_input = ComparisonInput(
#     ticket_id=extracted_output.ticket_id,
#     identified_endpoints=extracted_output.identified_endpoints,
#     existing_specifications=existing_specs
# )

# Step 4: Run Comparison Task
# comparison_crew = Crew(
#     agents=[api_analysis_agent],
#     tasks=[compare_api_task],
#     verbose=True
# )

# # Manually set the task context before running it
# compare_api_task.context = [comparison_input]

# inputs = {"existing_specification": existing_specs}

# Run the comparison process
# comparison_result = comparison_crew.kickoff(inputs=inputs)
# final_output = comparison_result.pydantic

# Print the final analysis report
# print(final_output)



# Run the workflow
# load_dotenv("./.env", override=True)
# track_crewai(project_name="jira_detection")
# result = jira_api_review_crew.kickoff()
# print(result.pydantic)