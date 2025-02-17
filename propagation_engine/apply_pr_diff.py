import subprocess
import os


def run_command(command, repo_path):
    """
    Run a shell command in the context of a repository.
    """
    try:
        result = subprocess.run(
            command, cwd=repo_path, text=True, check=True, capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")
        raise


def apply_diff(repo_path, diff_file, target_branch):
    """
    Apply a diff file to a specific branch in a Git repository.

    :param repo_path: Path to the Git repository
    :param diff_file: Path to the diff file
    :param target_branch: Branch where changes will be applied
    """
    # Ensure the repository exists
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        raise Exception(f"{repo_path} is not a valid Git repository")

    # Checkout the target branch
    print(f"Checking out branch {target_branch}...")
    run_command(["git", "checkout", target_branch], repo_path)

    # Apply the diff file
    print(f"Applying diff file: {diff_file}...")
    run_command(["git", "apply", diff_file], repo_path)

    # Check the status
    print("Checking status...")
    status = run_command(["git", "status"], repo_path)
    print(status)

    # Commit the changes
    print("Committing changes...")
    run_command(
        ["git", "commit", "-am", f"Applied changes from {diff_file}"], repo_path
    )

    # Push the changes
    print(f"Pushing changes to branch {target_branch}...")
    run_command(["git", "push", "origin", target_branch], repo_path)

    print("Diff file applied and pushed successfully!")


# Example Usage
if __name__ == "__main__":
    # Replace these values with your details
    repo_path = "/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/user-manager"  # Path to the local repository
    diff_file = "/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/pr_diff.diff"  # Path to the diff file
    target_branch = "usr/sakthivel_ganesan/replicate_added_phone_number_attribute"  # Branch to apply the diff

    try:
        apply_diff(repo_path, diff_file, target_branch)
    except Exception as e:
        print(f"An error occurred: {e}")
