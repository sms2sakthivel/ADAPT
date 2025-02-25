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
    # load_dotenv("/app/data/.env", override=True)
    load_dotenv("./.env", override=True)
    crew = OnboardingCrew()
    crew.run_demon()

def run_analysis_demon():
    print(f"Analysis Process (PID: {os.getpid()}) starting...")
    analysis_engine = AnalysisEngine()
    analysis_engine.run_demon()

def run_onboarding_server():
    print(f"Server Process (PID: {os.getpid()}) starting...")
    # load_dotenv("/app/data/.env", override=True)
    load_dotenv("./.env", override=True)
    uvicorn.run(app, host="0.0.0.0", port=9501)

def run_streamlit_dashboard():
    print(f"Streamlit Dashboard Process (PID: {os.getpid()}) starting...")
    os.system("streamlit run ./Dashboard.py --server.port 9503")


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


    # Run Streamlit Dashboard
    streamlit_dashboard = multiprocessing.Process(target=run_streamlit_dashboard)
    streamlit_dashboard.start()

    # Keep the main process alive (optional, depends on your needs)
    try:
      while True:
        time.sleep(1)  # Or perform other tasks in the main process if needed
    except KeyboardInterrupt:
      print("Shutting down...")
      onboarding_server.terminate()
      onboarding_fullfiller.terminate()
      analyser.terminate()
      streamlit_dashboard.terminate()
      print("All processes terminated.")