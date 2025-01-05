from typing import Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from central_system.database import engine
from .agent_output_model import OnboardingDataModel, ProjectDataModel
from central_system.database.onboarding import (
    Project,
    Service,
    Client,
    Endpoints,
    EndpointConsumers,
)


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
        with Session(self.engine) as session:
            try:
                # Step 1: Update Project Table
                project: Optional[Project] = (
                    session.query(Project)
                    .filter(Project.repository_url == self.meta_data.repository_url)
                    .first()
                )
                if not project:
                    new_project = Project(
                        name=self.data.project_name,
                        repository_url=self.meta_data.repository_url,
                    )
                    session.add(new_project)
                    session.commit()
                    project = new_project

                # Step 2: Update Services Table
                service: Optional[Service] = (
                    session.query(Service)
                    .filter(
                        and_(
                            Service.project_id == project.id,
                            Service.branch == self.meta_data.branch_name,
                        )
                    )
                    .first()
                )
                if not service:
                    new_service = Service(
                        project_id=project.id,
                        port=self.data.port,
                        branch=self.meta_data.branch_name,
                    )
                    session.add(new_service)
                    session.commit()
                    service = new_service

                # Step 3: Update Client Table
                client: Optional[Client] = (
                    session.query(Client)
                    .filter(
                        and_(
                            Client.project_id == project.id,
                            Client.branch == self.meta_data.branch_name,
                        )
                    )
                    .first()
                )
                if not client:
                    new_client = Client(
                        project_id=project.id, branch=self.meta_data.branch_name
                    )
                    session.add(new_client)
                    session.commit()
                    client = new_client

                # Step 4: Update Endpoints Table
                for exposed_endpoint in self.data.exposed_endpoints:
                    for method in exposed_endpoint.methods:
                        endpoint = (
                            session.query(Endpoints)
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
                            session.add(
                                Endpoints(
                                    service_id=service.id,
                                    endpoint_url=exposed_endpoint.endpoint,
                                    method=method.method,
                                    description=method.description,
                                )
                            )
                            session.commit()

                # Step 5: Update EndpointConsumer Table
                for consumed_endpoints in self.data.consumed_endpoints:
                    for method in consumed_endpoints.methods:
                        endpoint_db_data: Optional[Endpoints] = (
                            session.query(Endpoints)
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
                            session.query(EndpointConsumers)
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
                            session.add(
                                EndpointConsumers(
                                    endpoint_id=endpoint_db_data.id, client_id=client.id
                                )
                            )
                            session.commit()

                return (
                    True,
                    "Successfully Onboarded the service and its endpoints. EndpointConsumer entries created successfully.",
                )
            except Exception as e:
                print(f"Error during onboarding: {e}")
                session.rollback()
                return False, str(e)
