from ariadne import QueryType, MutationType
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from central_system.services import queries, mutations
from central_system.database import SessionLocal
from central_system.database.onboarding import (
    Repository,
    Service,
    Client,
    RepoBranch,
    Status,
    Endpoints,
    AffectedEndpoints,
    Status,
    ChangeOrigin,
    ChangeType,
)


repository_query = QueryType()
repository_mutation = MutationType()


@repository_query.field("repositories")
def resolve_repositories(_, info, page=1, size=100):
    with SessionLocal() as db:
        try:
            page = int(page)
            size = int(size)
            start = (page - 1) * size
            result = (
                db.query(Repository)
                .outerjoin(RepoBranch, Repository.id == RepoBranch.repository_id)
                .outerjoin(Service, RepoBranch.id == Service.repo_branches_id)
                .outerjoin(Client, RepoBranch.id == Client.repo_branches_id)
                .outerjoin(Endpoints, Service.id == Endpoints.service_id)
                .options(
                    joinedload(Repository.repo_branches)
                    .joinedload(RepoBranch.services)
                    .joinedload(Service.endpoints),
                    joinedload(Repository.repo_branches)
                    .joinedload(RepoBranch.clients)
                    .joinedload(Client.consumed_endpoints),
                )
                .offset(start)
                .limit(size)
                .all()
            )
            # Format the result
            print(result)
            repositories = []
            for repository in result:
                repo_branches = []
                for repo_branch in repository.repo_branches:
                    services = []
                    for service in repo_branch.services:
                        endpoints = [
                            {
                                "id": endpoint.id,
                                "url": endpoint.endpoint_url,
                                "method": endpoint.method,
                                "description": endpoint.description,
                                "specification": endpoint.specifications,
                            }
                            for endpoint in service.endpoints
                        ]
                        services.append(
                            {
                                "id": service.id,
                                "port": service.port,
                                "exposed_endpoints": endpoints,
                            }
                        )

                    clients = []
                    for client in repo_branch.clients:
                        consumed_endpoints = [
                            {
                                "id": endpoint.endpoint.id,
                                "url": endpoint.endpoint.endpoint_url,
                                "method": endpoint.endpoint.method,
                                "description": endpoint.endpoint.description,
                                "specification": endpoint.endpoint.specifications,
                            }
                            for endpoint in client.consumed_endpoints
                        ]
                        clients.append(
                            {
                                "id": client.id,
                                "consumed_endpoints": consumed_endpoints,
                            }
                        )

                    repo_branches.append(
                        {
                            "id": repo_branch.id,
                            "branch": repo_branch.branch,
                            "included_extensions": repo_branch.included_extensions,
                            "status": repo_branch.status.value,
                            "services": services,
                            "clients": clients,
                            "name": repo_branch.name,
                            "jira_instance_url": repo_branch.jira_instance_url,
                            "jira_project_key": repo_branch.jira_project_key,
                            "guid": repo_branch.guid,
                        }
                    )
                repositories.append(
                    {
                        "id": repository.id,
                        "url": repository.url,
                        "repo_branches": repo_branches,
                        "name": repository.name,
                        "jira_instance_url": repository.jira_instance_url,
                        "jira_project_key": repository.jira_project_key,
                        "guid": repository.guid,
                    }
                )
            return repositories
        finally:
            db.close()


@repository_query.field("repository")
def resolve_repository(_, info, id):
    with SessionLocal() as db:
        try:
            result = (
                db.query(Repository)
                .options(
                    joinedload(Repository.repo_branches)
                    .joinedload(RepoBranch.services)
                    .joinedload(Service.endpoints),
                    joinedload(Repository.repo_branches)
                    .joinedload(RepoBranch.clients)
                    .joinedload(Client.consumed_endpoints),
                )
                .filter(Repository.id == id)
                .first()
            )
            if not result:
                return None

            # Format the result
            repo_branches = []
            for repo_branch in result.repo_branches:
                services = []
                for service in repo_branch.services:
                    endpoints = [
                        {
                            "id": endpoint.id,
                            "url": endpoint.endpoint_url,
                            "method": endpoint.method,
                            "description": endpoint.description,
                            "specification": endpoint.specifications,
                        }
                        for endpoint in service.endpoints
                    ]
                    services.append(
                        {
                            "id": service.id,
                            "port": service.port,
                            "exposed_endpoints": endpoints,
                        }
                    )

                clients = []
                for client in repo_branch.clients:
                    consumed_endpoints = [
                        {
                            "id": endpoint.endpoint.id,
                            "url": endpoint.endpoint.endpoint_url,
                            "method": endpoint.endpoint.method,
                            "description": endpoint.endpoint.description,
                            "specification": endpoint.endpoint.specifications,
                        }
                        for endpoint in client.consumed_endpoints
                    ]
                    clients.append(
                        {
                            "id": client.id,
                            "consumed_endpoints": consumed_endpoints,
                        }
                    )

                repo_branches.append(
                    {
                        "id": repo_branch.id,
                        "branch": repo_branch.branch,
                        "included_extensions": repo_branch.included_extensions,
                        "status": repo_branch.status.value,
                        "services": services,
                        "clients": clients,
                        "name": repo_branch.name,
                        "jira_instance_url": repo_branch.jira_instance_url,
                        "jira_project_key": repo_branch.jira_project_key,
                        "guid": repo_branch.guid,
                    }
                )
            return {
                "id": result.id,
                "url": result.url,
                "repo_branches": repo_branches,
                "name": result.name,
                "jira_instance_url": result.jira_instance_url,
                "jira_project_key": result.jira_project_key,
                "guid": result.guid,
            }
        finally:
            db.close()


@repository_mutation.field("onboardRepository")
def resolve_onboard_repository(
    _, info, url: str, branch: str, included_extensions: list
):
    with SessionLocal() as db:
        try:
            repository = Repository(url=url)
            db.add(repository)
            db.commit()
            repo_branch = RepoBranch(
                repository_id=repository.id,
                branch=branch,
                included_extensions=included_extensions,
                status=Status.PENDING,
            )
            db.add(repo_branch)
            db.commit()
            return {
                "id": repository.id,
                "url": repository.url,
                "repo_branches": [
                    {
                        "id": repo_branch.id,
                        "branch": repo_branch.branch,
                        "included_extensions": repo_branch.included_extensions,
                        "status": repo_branch.status.value,
                        "services": [],
                        "clients": [],
                    }
                ],
            }
        except IntegrityError as ie:
            db.rollback()
            raise Exception("Repository already exists")
        finally:
            db.close()


@repository_mutation.field("notifyAffectedEndpoints")
def resolve_notify_affected_endpoints(_, info, url: str, method: str, changeType: str, description: str, reason: str, changeOrigin: str, originUniqueID: str, changeOriginURL: str):
    with SessionLocal() as db:
        try:
            # get the endpoint using url and method.
            endpoint = db.query(Endpoints).filter(Endpoints.endpoint_url == url, Endpoints.method == method).first()
            if not endpoint:
                raise Exception("Endpoint not found")
            affected_endpoint = db.query(AffectedEndpoints).filter(AffectedEndpoints.endpoint_id == endpoint.id, AffectedEndpoints.change_origin == ChangeOrigin(changeOrigin) ,AffectedEndpoints.origin_unique_id == originUniqueID, AffectedEndpoints.change_type == ChangeType(changeType)).first()
            if affected_endpoint is None:
                # insert into the affected_endpoints table
                affected_endpoint = AffectedEndpoints(
                    endpoint_id=endpoint.id,
                    change_type=ChangeType(changeType),
                    description=description,
                    reason=reason,
                    status = Status.PENDING,
                    change_origin = ChangeOrigin(changeOrigin),
                    origin_unique_id = originUniqueID,
                    change_origin_url = changeOriginURL
                )
                db.add(affected_endpoint)
                db.commit()
            else:
                affected_endpoint.description = affected_endpoint.description + "\n" + description
                affected_endpoint.reason = affected_endpoint.reason + "\n" + reason
                affected_endpoint.status = Status.UPDATED
                db.add(affected_endpoint)
                db.commit()
            return {
                "id": affected_endpoint.id,
                "url": affected_endpoint.endpoint.endpoint_url,
                "method": affected_endpoint.endpoint.method,
                "changeType": affected_endpoint.change_type,
                "description": affected_endpoint.description,
                "reason": affected_endpoint.reason,
                "status": affected_endpoint.status,
                "changeOrigin": affected_endpoint.change_origin,
            }
        finally:
            db.close()


queries.append(repository_query)
mutations.append(repository_mutation)
