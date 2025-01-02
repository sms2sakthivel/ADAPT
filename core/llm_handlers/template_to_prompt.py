import json
import requests
import zipfile
import io

def get_branch_source(repo: str, branch: str, include_extensions: list = None) -> str:
    """
    Fetch the source content of a branch in a GitHub repository and save it as a single text file.
    
    Args:
        repo (str): The GitHub repository in the format "owner/repo".
        branch (str): The branch name to fetch the source for.
        include_extensions (list): List of file extensions to include (e.g., ['.py', '.txt']). If None, include all files.
        output_file (str): The name of the output text file.

    Returns:
        str: Path to the generated text file.
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
                if file_info.filename.endswith('/'):  # Skip directories
                    continue
                
                # Filter by specified extensions
                if include_extensions:
                    if not any(file_info.filename.endswith(ext) for ext in include_extensions):
                        continue
                
                # Read and collect file content
                with z.open(file_info.filename) as file:
                    try:
                        content = file.read().decode('utf-8', errors='ignore')  # Decode file content
                        collected_content.append(f"--- {file_info.filename} ---\n{content}\n")
                    except Exception as e:
                        print(f"Failed to process {file_info.filename}: {e}")

        return "\n".join(collected_content)
    except requests.exceptions.RequestException as e:
        return f"Error fetching branch source: {e}"
    except zipfile.BadZipFile:
        return "Error: Invalid ZIP archive."

def generate_prompt_from_template(template_path: str, repo: str, branch: str, included_extensions: list) -> str:
    with open(template_path, "r") as template:
        prompt_template = json.load(template)
    
    source = get_branch_source(repo, branch, included_extensions)
    source = json.dumps(source)

    prompt = f"# Purpose:\n{prompt_template['purpose']}\n\n"
    prompt += f"# Instructions:\n{prompt_template['instructions']}\n\n"
    prompt += f"# Example json output: ```JSON\n{prompt_template['example_json_output']}\n```\n\n"
    prompt += f"# Source Code:\n {source}\n\n"
    return json.dumps(prompt)

def get_system_prompt(template_path: str) -> str:
    with open(template_path, "r") as template:
        prompt_template = json.load(template)
    return prompt_template['system']

if __name__ == "__main__":
    output = generate_prompt_from_template("/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/ADAPT/central-system/onboarding/prompt-templates/extractinformations.json","sms2sakthivel/payment-manager", "master",[".go",".project.json"])
    print(output)

