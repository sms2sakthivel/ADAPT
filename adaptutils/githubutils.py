import requests
import zipfile, io
from github import Github, PullRequest


class GitHubApp:
    def __init__(self, auth_token: str):
        self.g = Github(auth_token)

    def get_pr(self, owner: str, repo: str, pr_number: int) -> PullRequest:
        # Step 1: Access the repository
        repository = self.g.get_repo(f"{owner}/{repo}")

        # Step 2: Get the pull request
        pr = repository.get_pull(pr_number)
        return pr

    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        # Step 1: Access the repository
        repository = self.g.get_repo(f"{owner}/{repo}")

        # Step 2: Get the pull request
        pr = repository.get_pull(pr_number)

        # Step 3: Fetch the diff using the diff_url attribute
        response = requests.get(
            pr.diff_url, headers={"Accept": "application/vnd.github.v3.diff"}
        )

        # Step 4: Check for a successful response
        if response.status_code == 200:
            return response.text  # Return the raw diff text
        else:
            print(f"Error: {response.status_code}")
            return ""

    def get_pr_diff_from_diff_url(self, diff_url: str):
        # Step 1: Use the diff_url to make a GET request for the diff content
        response = requests.get(
            diff_url, headers={"Accept": "application/vnd.github.v3.diff"}
        )

        # Step 2: Check for a successful response
        if response.status_code == 200:
            return response.text  # Return the raw diff text
        else:
            print(f"Error: {response.status_code}")
            return ""

    def get_repo_branch_source(
        self,
        owner: str,
        repo: str,
        branch: str,
        include_extensions: list = None,
    ) -> dict:
        try:
            # Step 1: Access the repository
            # repository = self.g.get_repo(f"{owner}/{repo}")

            # Step 2: Get the zipball archive link for the branch
            # zip_url = repository.get_archive_link("zipball", ref=branch)
            zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

            # Step 3: Fetch the zipped source code
            response = requests.get(zip_url)
            response.raise_for_status()

            # Step 4: Load the zip archive into memory and extract file contents
            source_code = {}
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for file_info in z.infolist():
                    if file_info.filename.endswith("/"):  # Skip directories
                        continue

                    # Step 4.1 Extract only specific file extensions (if specified)
                    if include_extensions and not any(
                        file_info.filename.endswith(ext) for ext in include_extensions
                    ):
                        continue

                    # Step 4.2: Read file content
                    with z.open(file_info.filename) as file:
                        try:
                            content = file.read().decode("utf-8", errors="ignore")
                            source_code[file_info.filename] = content
                        except Exception as e:
                            print(f"Failed to process {file_info.filename}: {e}")

            return source_code

        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch zipball: {e}"}
        except zipfile.BadZipFile:
            return {"error": "Invalid ZIP archive."}
        except Exception as e:
            return {"error": str(e)}
