import requests
import zipfile
import io
import json
from github import Github


def get_branch_source(repo: str, branch: str, include_extensions: list = None) -> str:
    """
    Fetch the source content of a branch in a GitHub repository and save it as a single text file.

    Args:
        repo (str): The GitHub repository in the format "owner/repo".
        branch (str): The branch name to fetch the source for.
        include_extensions (list): List of file extensions to include (e.g., ['.py', '.txt']). If None, include all files.

    Returns:
        str: output string
    """
    # GitHub API URL to get branch content
    archive_url = f"https://api.github.com/repos/{repo}/zipball/{branch}"

    try:
        # Fetch the zipped source code
        response = requests.get(archive_url)
        response.raise_for_status()

        # Load the zip archive into memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Filter files by extension and collect content
            collected_content = []
            for file_info in z.infolist():
                if file_info.filename.endswith("/"):  # Skip directories
                    continue

                # Filter by specified extensions
                if include_extensions:
                    if not any(
                        file_info.filename.endswith(ext) for ext in include_extensions
                    ):
                        continue

                # Read and collect file content
                with z.open(file_info.filename) as file:
                    try:
                        content = file.read().decode(
                            "utf-8", errors="ignore"
                        )  # Decode file content
                        collected_content.append(
                            f"--- {file_info.filename} ---\n{content}\n"
                        )
                    except Exception as e:
                        print(f"Failed to process {file_info.filename}: {e}")

        return "\n".join(collected_content)
    except requests.exceptions.RequestException as e:
        return f"Error fetching branch source: {e}"
    except zipfile.BadZipFile:
        return "Error: Invalid ZIP archive."


def get_branch_source_dump(repo: str, branch: str, included_extensions: list) -> str:
    source = get_branch_source(repo, branch, included_extensions)
    return json.dumps(source)


if __name__ == "__main__":
    # Replace these values with your details
    GITHUB_REPO = "sms2sakthivel/user-manager"
    BRANCH = "master"
    INCLUDED_EXTENSIONS = [".go", ".project.json"]

    # Fetch and save the source content
    source_dump = get_branch_source_dump(GITHUB_REPO, BRANCH, INCLUDED_EXTENSIONS)
    with open("source_dump.txt", "w") as file:
        file.write(source_dump)

    print("Source content saved as source_dump.txt")
