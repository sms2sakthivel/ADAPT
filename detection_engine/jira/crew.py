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
        if jira_data_dict["status"] not in ["Done", "Completed", "Accepted"]:
            print(f"Event Skipped for status {jira_data_dict['status']}")
            return True, "SKIPPED"
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
