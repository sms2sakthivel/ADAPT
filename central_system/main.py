import os
import multiprocessing
import time

from central_system.services.app import app
import uvicorn
from central_system.onboarding.onboard import OnboardingCrew
from central_system.analysis.analysis import AnalysisEngine
from dotenv import load_dotenv

def run_onboarding_crew_demon():
    print(f"Fullfiller Process (PID: {os.getpid()}) starting...")
    load_dotenv("/app/data/.env", override=True)
    crew = OnboardingCrew()
    crew.run_demon()

def run_analysis_demon():
    print(f"Analysis Process (PID: {os.getpid()}) starting...")
    analysis_engine = AnalysisEngine()
    analysis_engine.run_demon()

def run_onboarding_server():
    print(f"Server Process (PID: {os.getpid()}) starting...")
    load_dotenv("/app/data/.env", override=True)
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    print(f"Main Process (PID: {os.getpid()}) starting...")

    # Run Onboarding Server
    onboarding_server = multiprocessing.Process(target=run_onboarding_server)
    onboarding_server.start()

    # Run Background Fullfiller Demon
    onboarding_fullfiller = multiprocessing.Process(target=run_onboarding_crew_demon)
    onboarding_fullfiller.start()

    # Run Background Analysis Demon
    analyser = multiprocessing.Process(target=run_analysis_demon)
    analyser.start()

    # Keep the main process alive (optional, depends on your needs)
    try:
      while True:
        time.sleep(1)  # Or perform other tasks in the main process if needed
    except KeyboardInterrupt:
      print("Shutting down...")
      onboarding_server.terminate()
      onboarding_fullfiller.terminate()
      analyser.terminate()
      print("All processes terminated.")