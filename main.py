# from central_system.services.app import app
# import uvicorn
from central_system.onboarding.onboard import OnboardingCrew
from dotenv import load_dotenv
import os
from datetime import datetime

from adaptutils.githubutils import GitHubApp
from detection_engine.workflow import DetectionCrew

load_dotenv("./.env", override=True)

# if __name__ == "__main__":
#     os.environ["OPENAI_API_KEY"] = (
#         "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"
#     )
#     os.environ["MODEL"] = "gpt-4o-mini"

#     crew = OnboardingCrew()
#     crew.run_demon()
#     # uvicorn.run(app, host="0.0.0.0", port=8001)


# if __name__ == "__main__":
#     # Example Usage
#     GITHUB_OWNER = "sms2sakthivel"
#     GITHUB_REPO = "user-manager"
#     PR_NUMBER = 1  # Replace with the PR number
#     GITHUB_TOKEN = "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"

#     ghapp = GitHubApp(GITHUB_TOKEN)
#     source_files = ghapp.get_repo_branch_source(
#         branch="master",
#         repo_name=f"{GITHUB_OWNER}/{GITHUB_REPO}",
#         include_extensions=[".go", ".project.json"],
#     )

#     with open("source.txt", "w") as file:
#         for path, content in source_files.items():
#             file.write(f"--- {path} ---\n{content}\n")

# from detection_engine.detection_engine import DetectionEngine

# if __name__ == "__main__":

#     GITHUB_OWNER = "sms2sakthivel"
#     GITHUB_REPO = "user-manager"
#     PR_NUMBER = 1  # Replace with the PR number
#     de = DetectionEngine()
#     time = datetime.now()
#     de.detect_pr_interface_changes(
#         repo_owner=GITHUB_OWNER, repo_name=GITHUB_REPO, pr_number=PR_NUMBER
#     )
#     print(datetime.now() - time)


if __name__ == "__main__":
    load_dotenv(
        "/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/ADAPT/.env",
        override=True,
    )
    crew = DetectionCrew()
    crew.detect(repo_owner="sms2sakthivel", repo_name="user-manager", pr_number=1)
    # uvicorn.run(app, host="0.0.0.0", port=8001)
