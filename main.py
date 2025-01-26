# from central_system.services.app import app
# import uvicorn
from central_system.onboarding.onboard import OnboardingCrew
from dotenv import load_dotenv
import os

load_dotenv(".env", override=True)

if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = (
        "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"
    )
    os.environ["MODEL"] = "gpt-4o-mini"

    crew = OnboardingCrew()
    crew.run_demon()
    # uvicorn.run(app, host="0.0.0.0", port=8001)
