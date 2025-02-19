from fastapi import FastAPI, Request
from detection_engine.jira.crew import JIRADetectionCrew
from dotenv import load_dotenv
# from opik.integrations.crewai import track_crewai

load_dotenv("./.env", override=True)
# track_crewai(project_name="jira_detection")

app = FastAPI()

@app.post("/jira-webhook")
async def jira_webhook(request: Request):
    data = await request.json()
    print("Received Jira Event:", data)
    crew = JIRADetectionCrew()
    crew.detect(data)
    return {"message": "Event received"}
