from typing import Tuple, Optional
from sqlalchemy import and_
import json

from central_system.database import engine
from .agent_output_model import OnboardingDataModel, ProjectDataModel
from central_system.database.onboarding import (
    Service,
    Client,
    Endpoints,
    EndpointConsumers,
    Repository,
    RepoBranch,
)
from central_system.database import SessionLocal


class OnboardingHandler:
    def __init__(self, meta_data: ProjectDataModel, engine=engine):
        self.engine = engine
        self.data: OnboardingDataModel
        self.meta_data: ProjectDataModel = meta_data

    def validate_data(self, data: str) -> Tuple[bool, str]:
        try:
            self.data = OnboardingDataModel.model_validate_json(data)
        except Exception as e:
            return False, f"Validation Error: {e}"
        return True, None

    def onboard(self, data: str) -> Tuple[bool, str]:
        # Step 1: validate the Agent Output data
        ok, error = self.validate_data(data)
        if not ok:
            return False, error

        # create entry in projects table if the UUID does not exist already
        with SessionLocal() as db:
            try:
                # Step 1: Retrieve the repo details
                repository_branch, repository = (
                    db.query(RepoBranch, Repository)
                    .join(Repository, RepoBranch.repository_id == Repository.id)
                    .filter(Repository.url == self.meta_data.repository_url)
                    .first()
                )
                if not repository:
                    raise Exception(
                        f"Repository {self.meta_data.repository_url} not found in the database."
                    )
                elif not repository_branch:
                    raise Exception(
                        f"Branch {self.meta_data.branch_name} not found in the database."
                    )

                # Step 1.1: Update Repository
                repository.name = self.data.repository.project_name
                repository.guid = self.data.repository.guid
                repository.jira_instance_url = self.data.repository.jira_instance_url
                repository.jira_project_key = self.data.repository.jira_project_key

                repository_branch.name = self.data.branch.project_name
                repository_branch.guid = self.data.branch.guid
                repository_branch.jira_instance_url = self.data.branch.jira_instance_url
                repository_branch.jira_project_key = self.data.branch.jira_project_key

                db.add(repository)
                db.add(repository_branch)
                db.commit()

                # Step 2: Update Services Table
                service: Optional[Service] = (
                    db.query(Service)
                    .filter(Service.repo_branches_id == repository_branch.id)
                    .first()
                )
                if not service:
                    new_service = Service(
                        repo_branches_id=repository_branch.id,
                        port=self.data.port,
                    )
                    db.add(new_service)
                    db.commit()
                    service = new_service

                # Step 3: Update Client Table
                client: Optional[Client] = (
                    db.query(Client)
                    .filter(Client.repo_branches_id == repository_branch.id)
                    .first()
                )
                if not client:
                    new_client = Client(repo_branches_id=repository_branch.id)
                    db.add(new_client)
                    db.commit()
                    client = new_client

                # Step 4: Update Endpoints Table
                for exposed_endpoint in self.data.exposed_endpoints:
                    for method in exposed_endpoint.methods:
                        endpoint = (
                            db.query(Endpoints)
                            .filter(
                                and_(
                                    Endpoints.service_id == service.id,
                                    Endpoints.endpoint_url == exposed_endpoint.endpoint,
                                    Endpoints.method == method.method,
                                )
                            )
                            .first()
                        )
                        if not endpoint:
                            db.add(
                                Endpoints(
                                    service_id=service.id,
                                    endpoint_url=exposed_endpoint.endpoint,
                                    method=method.method,
                                    description=method.description,
                                    specifications=json.dumps(method.specification),
                                )
                            )
                            db.commit()

                # Step 5: Update EndpointConsumer Table
                for consumed_endpoints in self.data.consumed_endpoints:
                    for method in consumed_endpoints.methods:
                        endpoint_db_data: Optional[Endpoints] = (
                            db.query(Endpoints)
                            .filter(
                                and_(
                                    Endpoints.endpoint_url
                                    == consumed_endpoints.endpoint,
                                    Endpoints.method == method.method,
                                )
                            )
                            .first()
                        )
                        if not endpoint_db_data:
                            # TODO: Add this entry into a missing endpoint table and process it once the missing endpoint is added to the Endpoints table
                            print(
                                "Skipping the creation of EndpointConsumer entry for endpoint: {consumed_endpoints.endpoint} and method: {method.method}.  Endpoint does not exist in Endpoints table.  Skipping this step."
                            )
                            # return False, "Failed to create EndpointConsumer entry"
                            continue

                        endpoint: Optional[Endpoints] = (
                            db.query(EndpointConsumers)
                            .filter(
                                and_(
                                    EndpointConsumers.endpoint_id
                                    == endpoint_db_data.id,
                                    EndpointConsumers.client_id == client.id,
                                )
                            )
                            .first()
                        )
                        if not endpoint:
                            db.add(
                                EndpointConsumers(
                                    endpoint_id=endpoint_db_data.id, client_id=client.id
                                )
                            )
                            db.commit()

                return (
                    True,
                    "Successfully Onboarded the service and its endpoints. EndpointConsumer entries created successfully.",
                )
            except Exception as e:
                print(f"Error during onboarding: {e}")
                db.rollback()
                return False, str(e)
