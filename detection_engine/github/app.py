from detection_engine.github.crew import GithubDetectionCrew
from dotenv import load_dotenv
import os



if __name__ == "__main__":
    load_dotenv("/app/data/.env", override=True)
    
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")
    pr_number = int(os.getenv("PR_NUMBER"))

    print(f"Processing PR #{pr_number} in {repo_owner}/{repo_name}")
    
    crew = GithubDetectionCrew()
    crew.detect(repo_owner=repo_owner, repo_name=repo_name, pr_number=pr_number)
