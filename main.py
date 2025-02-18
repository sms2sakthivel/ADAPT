import os
import multiprocessing
import time

from central_system.services.app import app
import uvicorn
from central_system.onboarding.onboard import OnboardingCrew
from dotenv import load_dotenv

def run_onboarding_crew_daemon():
    load_dotenv(".env", override=True)
    crew = OnboardingCrew()
    crew.run_demon()

def run_onboarding_server():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    print(f"Main Process (PID: {os.getpid()}) starting...")
    load_dotenv(".env", override=True)

    # Run Onboarding Server
    onboarding_server = multiprocessing.Process(target=run_onboarding_server)
    onboarding_server.start()

    # Run Background Daemon
    onboarding_fullfiller = multiprocessing.Process(target=run_onboarding_crew_daemon)
    onboarding_fullfiller.start()

        # Keep the main process alive (optional, depends on your needs)
    try:
      while True:
        time.sleep(1)  # Or perform other tasks in the main process if needed
    except KeyboardInterrupt:
      print("Shutting down...")
      onboarding_server.terminate()
      onboarding_fullfiller.terminate()
      print("All processes terminated.")