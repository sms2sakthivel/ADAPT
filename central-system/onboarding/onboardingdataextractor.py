import json
from schema import OnboardingSchema
from 

class OnboardingDataExtractor:
    def __init__(self, repository: str, branch: str, included_files: list[str], excluded_files: list[str]):
        self.repository = repository
        self.branch = branch
        self.included_files = included_files
        self.excluded_files = excluded_files
        with open("prompt_templates/extract_onboarding_informations.json") as template_file:
            self.prompt_template = json.loads(template_file.read())
    
    def extract_onboarding_data() -> OnboardingSchema:
        
