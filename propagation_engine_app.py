import os
import time
import multiprocessing
from dotenv import load_dotenv

from propagation_engine.github.crew import GithubPropagationCrew
from propagation_engine.jira.crew import JiraPropagationCrew

def run_jira_propagation_crew():
    print(f"JIRA Propagator Process (PID: {os.getpid()}) starting...")
    # load_dotenv("/app/data/.env", override=True)
    load_dotenv("./.env", override=True)
    crew = JiraPropagationCrew()
    while True:
        time.sleep(1)
        crew.propagate()

def run_github_propagation_crew():
    print(f"Github Propagator Process (PID: {os.getpid()}) starting...")
    # load_dotenv("/app/data/.env", override=True)
    load_dotenv("./.env", override=True)
    crew = GithubPropagationCrew()
    while True:
        time.sleep(1)
        crew.propagate()

if __name__ == "__main__":
    load_dotenv("./.env", override=True)


    # Run Jira Propagation Crew
    jira_propagation_crew = multiprocessing.Process(target=run_jira_propagation_crew)
    jira_propagation_crew.start()

    # Run Github Propagation Crew
    github_propagation_crew = multiprocessing.Process(target=run_github_propagation_crew)
    github_propagation_crew.start()

    # Keep the main process alive (optional, depends on your needs)
    try:
      while True:
        time.sleep(1)  # Or perform other tasks in the main process if needed
    except KeyboardInterrupt:
      print("Shutting down...")
      jira_propagation_crew.terminate()
      github_propagation_crew.terminate()
      print("All processes terminated.")