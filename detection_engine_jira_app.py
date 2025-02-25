import os
import uvicorn
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
    # print("Received Jira Event")
    crew = JIRADetectionCrew()
    _, status = crew.detect(data)
    return {"message": status}


if __name__ == "__main__":
    print(f"Server Process (PID: {os.getpid()}) starting...")
    # load_dotenv("/app/data/.env", override=True)
    load_dotenv("./.env", override=True)
    uvicorn.run(app, host="0.0.0.0", port=9502)