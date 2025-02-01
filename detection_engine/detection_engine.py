import os

from adaptutils.githubutils import GitHubApp


class DetectionEngine:
    def __init__(self):
        self.github_app = GitHubApp(auth_token=os.getenv("GITHUB_API_TOKEN"))

    def detect_pr_interface_changes(
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

        # Step 4: Write the Base Branch Source and PR Diff in a file
        base_branch_source_code = ""
        base_branch_source_code += "=" * 50 + "\n"
        base_branch_source_code += "Base Branch Source\n"
        base_branch_source_code += "=" * 50 + "\n"
        for path, content in base_branch_source.items():
            base_branch_source_code += f"--- {path} ---\n{content}\n"
        base_branch_source_code += "\n\n"

        # Add PR diff to the string
        diff_str = ""
        diff_str += "=" * 50 + "\n"
        diff_str += "PR Diff\n"
        diff_str += "=" * 50 + "\n"
        diff_str += diff
        return base_branch_source_code, diff_str
        # with open("Context.txt", "w") as file:
        #     file.write("".join(["=" for _ in range(50)]) + "\n")
        #     file.write("Base Branch Source\n")
        #     file.write("".join(["=" for _ in range(50)]) + "\n")
        #     for path, content in base_branch_source.items():
        #         file.write(f"--- {path} ---\n{content}\n")
        #     file.write("\n\n")
        #     file.write("".join(["=" for _ in range(50)]) + "\n")
        #     file.write("PR Diff\n")
        #     file.write("".join(["=" for _ in range(50)]) + "\n")
        #     file.write(diff)
