import os
import requests
import pprint

from adaptutils.githubutils import GitHubApp


class DetectionEngine:
    def __init__(self):
        self.github_app = GitHubApp(auth_token=os.getenv("GITHUB_API_TOKEN"))

    def get_pr_diff_and_base_branch_source(
        self, repo_owner: str, repo_name: str, pr_number: int
    ) -> str:

        # Step 1: Get the PR Object
        pr = self.github_app.get_pr(repo_owner, repo_name, pr_number)

        # Step 2: Get the Base Branch Source
        base_branch_source = self.github_app.get_repo_branch_source(
            repo_owner,
            repo_name,
            pr.base.ref,
            include_extensions=[".go", ".project.json"],
        )
        # Step 3: Get the pull request diff
        diff = self.github_app.get_pr_diff_from_diff_url(pr.diff_url)

        # Step 4: Return the base branch source and diff
        base_branch_source_code = ""
        base_branch_source_code += "=" * 50 + "\n"
        base_branch_source_code += "Base Branch Source\n"
        base_branch_source_code += "=" * 50 + "\n"
        for path, content in base_branch_source.items():
            base_branch_source_code += f"--- {path} ---\n{content}\n"
        base_branch_source_code += "\n\n"

        diff_str = ""
        diff_str += "=" * 50 + "\n"
        diff_str += "PR Diff\n"
        diff_str += "=" * 50 + "\n"
        diff_str += diff
        return base_branch_source_code, diff_str
    
    def test_connectivity(self):
        service_url = os.environ["SERVICE_URL"]
        url = f"{service_url}/graphql"
        print(f"URL: {url}")

        payload = "{\"query\":\"query{\\n  repository(id:1) {\\n    id\\n    url\\n    repo_branches{\\n      id\\n      branch\\n      included_extensions\\n      status\\n      services {\\n        id\\n        port\\n        exposed_endpoints{\\n          url\\n          method\\n        }\\n      }\\n      clients {\\n       id\\n        consumed_endpoints{\\n          url\\n          method\\n        }\\n      }\\n    }\\n  }\\n}\"}"
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        pprint.pprint(response.json())