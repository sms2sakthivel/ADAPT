import os
import requests
import zipfile, io
import tempfile
from typing import Tuple
from github import Github, PullRequest
import git



class GitHubApp:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
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

    def prepare_repo_feature_branch(self, temp_dir: str, owner: str, repository: str, base_branch: str, feature_branch: str) -> Tuple[bool, git.Repo]:
        """Clone repo, checkout to feature branch"""
        repo_url = f"git@github.com:{owner}/{repository}.git"
        print(f"Cloning repository {owner}/{repository} into {temp_dir}...")

        # Clone repository
        repo_path = os.path.join(temp_dir, repository)
        repo = git.Repo.clone_from(repo_url, repo_path)

        # Fetch the latest changes
        repo.git.fetch()

        # Ensure we are on the latest base branch
        print(f"Checking out base branch {base_branch}...")
        repo.git.checkout(base_branch)
        repo.git.pull("origin", base_branch)

        # Create and checkout new feature branch from base branch
        print(f"Creating new branch {feature_branch} from {base_branch}...")
        new_branch = repo.create_head(feature_branch)
        repo.head.reference = new_branch
        repo.head.reset(index=True, working_tree=True)
        return True, repo

    def apply_diff(self, repo: git.Repo, diff_file: str) -> bool:
        # Apply the diff
        diff_path = os.path.abspath(diff_file)
        print(f"Applying diff from {diff_path}...")
        repo.git.apply("--verbose", "--whitespace=fix", diff_path, ignore_whitespace=True)
        print("Patch Applied Successfully...!")
        return True
    
    def commit(self, repo: git.Repo, commit_message: str) -> bool:
        # Commit and push changes
        print("Committing changes...")
        repo.git.add(update=True)
        repo.index.commit(commit_message)
        print("Changes Committed Successfully...!")
        return True

    def push(self, repo: git.Repo, feature_branch: str) -> bool:
        print(f"Pushing changes to remote branch {feature_branch}...")
        repo.remote(name="origin").push(feature_branch)
        print("Changes pushed successfully!")
        return True

    def create_pull_request(self, owner: str, repository: str, title: str, description: str, feature_branch: str, base_branch: str) -> Tuple[bool, int, str]:
        repo = self.g.get_repo(f"{owner}/{repository}")
        # Create a pull request
        print("Creating a Pull Request...")
        pr = repo.create_pull(
            title=title,
            body=description,
            head=feature_branch,
            base=base_branch
        )
        print(f"Pull Request Created: {pr.html_url} and PR No: {pr.id}")
        return True, pr.id, pr.html_url

    def apply_diff_and_raise_pr(self, owner: str, repository: str, feature_branch: str, base_branch: str, commit_message: str, pr_title: str, pr_description: str, diff_file_path: str = "", diff_str: str = "") -> Tuple[bool, int, str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            ok, repo = self.prepare_repo_feature_branch(temp_dir, owner, repository, base_branch, feature_branch)
            if not ok:
                return False, -1, ""
            if diff_str:
                diff_file_path = os.path.join(temp_dir, "pr.diff")
                with open(diff_file_path, "w") as file:
                    file.write(diff_str)
                                
            ok = self.apply_diff(repo=repo, diff_file=diff_file_path)
            if not ok:
                return False, -1, ""
            
            ok = self.commit(repo=repo, commit_message=commit_message)
            if not ok:
                return False, -1, ""

            ok = self.push(repo=repo, feature_branch= feature_branch)
            if not ok:
                return False, -1, ""

            ok, pr_number, pr_url = self.create_pull_request(
                owner= owner,
                repository= repository,
                base_branch=base_branch,
                feature_branch= feature_branch,
                title= pr_title,
                description= pr_description,
            )
            if not ok:
                return False, pr_number, pr_url
        
        return True, pr_number, pr_url

if __name__ == "__main__":
    app = GitHubApp(auth_token="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")
    app.apply_diff_and_raise_pr(
            owner= "sms2sakthivel",
            repository= "order-manager",
            feature_branch= "feature/update-user-response-model",
            base_branch= "master",
            commit_message= "Remove user_id and user_name from UserResponse model to align with API changes",
            # diff_str='diff --git a/users/model/userapi.go b/users/model/userapi.go\nindex 70782a5..d4d172c 100644\n--- a/users/model/userapi.go\n+++ b/users/model/userapi.go\n@@ -1,31 +1,34 @@\n package model\n\n \n type UserCreateRequest struct {\n-	Name     string `json:"name"`\n-	Email    string `json:"email"`\n-	Username string `json:"user_name"`\n-	Password string `json:"password"`\n+	Name        string `json:"name"`\n+	Email       string `json:"email"`\n+	Username    string `json:"user_name"`\n+	Password    string `json:"password"`\n+	PhoneNumber string `json:"phone_number"`\n }\n \n type UserUpdateRequest struct {\n-	ID       uint   `json:"user_id"`\n-	Name     string `json:"name"`\n-	Email    string `json:"email"`\n-	Username string `json:"user_name"`\n-	Password string `json:"password"`\n+	ID          uint   `json:"user_id"`\n+	Name        string `json:"name"`\n+	Email       string `json:"email"`\n+	Username    string `json:"user_name"`\n+	Password    string `json:"password"`\n+	PhoneNumber string `json:"phone_number"`\n }\n \n type UserResponse struct {\n-	ID       uint   `json:"user_id"`\n-	Name     string `json:"name"`\n-	Email    string `json:"email"`\n-	Username string `json:"user_name"`\n+	ID          uint   `json:"user_id"`\n+	Name        string `json:"name"`\n+	Email       string `json:"email"`\n+	Username    string `json:"user_name"`\n+	PhoneNumber string `json:"phone_number"`\n }\n \n func (ucr *UserCreateRequest) GetDBObject() *User {\n-	return &User{Name: ucr.Name, Email: ucr.Email, Username: ucr.Username, PasswordHash: ucr.Password}\n+	return &User{Name: ucr.Name, Email: ucr.Email, Username: ucr.Username, PasswordHash: ucr.Password, PhoneNumber: ucr.PhoneNumber}\n }\n \n func (uur *UserUpdateRequest) GetDBObject() *User {\n-	return &User{ID: uur.ID, Name: uur.Name, Email: uur.Email, Username: uur.Username, PasswordHash: uur.Password}\n+	return &User{ID: uur.ID, Name: uur.Name, Email: uur.Email, Username: uur.Username, PasswordHash: uur.Password, PhoneNumber: uur.PhoneNumber}\n }\ndiff --git a/users/model/userdb.go b/users/model/userdb.go\nindex 4d16c87..df72d85 100644\n--- a/users/model/userdb.go\n+++ b/users/model/userdb.go\n@@ -9,8 +9,9 @@ type User struct {\n 	Email        string `gorm:"unique;not null"`\n 	Username     string `gorm:"unique;not null"`\n 	PasswordHash string `gorm:"not null"`\n+	PhoneNumber  string `gorm:"not null"`\n }\n \n func (user *User) GetAPIResponseObject() *UserResponse {\n-	return &UserResponse{ID: user.ID, Name: user.Name, Email: user.Email, Username: user.Username}\n+	return &UserResponse{ID: user.ID, Name: user.Name, Email: user.Email, Username: user.Username, PhoneNumber: user.PhoneNumber}\n }\n',
            diff_file_path="/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/ADAPT/pr-diff-13.diff",
            pr_title="Align UserResponse model with updated API specification",
            pr_description= "The UserResponse model has been updated to remove the user_id and user_name fields as per the new API specification. This change is necessary as the client code depends on this structure to retrieve user details. Without these modifications, the client may face integration failures when trying to communicate with the updated API.",
    )