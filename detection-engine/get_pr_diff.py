import requests


def get_pr_diff(owner, repo, pr_number, token):
    """
    Fetch the diff file for a GitHub Pull Request.

    :param owner: Repository owner (username or organization)
    :param repo: Repository name
    :param pr_number: Pull Request number
    :param token: GitHub Personal Access Token
    :return: Diff content as a string
    """
    # GitHub API URL for the PR
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    # Headers for the request
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",  # Request the diff format
    }

    # Make the API call
    response = requests.get(url, headers=headers)

    # Check for errors
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(
            f"Failed to fetch diff: {response.status_code} - {response.text}"
        )


# Example usage
if __name__ == "__main__":
    # Replace these values with your details
    GITHUB_OWNER = "sms2sakthivel"
    GITHUB_REPO = "user-manager"
    PR_NUMBER = 1  # Replace with the PR number
    GITHUB_TOKEN = "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"

    try:
        diff_content = get_pr_diff(GITHUB_OWNER, GITHUB_REPO, PR_NUMBER, GITHUB_TOKEN)
        # Save to a file
        with open("pr_diff.diff", "w") as file:
            file.write(diff_content)
        print("Diff file saved as pr_diff.diff")
    except Exception as e:
        print(e)
