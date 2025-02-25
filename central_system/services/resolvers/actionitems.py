import json
from datetime import datetime
from typing import Tuple, List
from ariadne import QueryType, MutationType
from central_system.services import queries, mutations
from central_system.database import SessionLocal
from central_system.services.model import AffectedClient, MetaData, GithubProject, JiraProject

from central_system.database.onboarding import (
    ActionItems,
    ActionType,
    Status,
)

action_item_query = QueryType()
action_item_mutation = MutationType()

@action_item_query.field("actionItems")
def resolve_action_items(_, info, type: str = "", propagationStatus: str = "", page=1, size=100):
    with SessionLocal() as db:
        try:
            page = int(page)
            size = int(size)
            start = (page - 1) * size

            query = db.query(ActionItems)
            if type:
                query = query.filter(ActionItems.action_type == ActionType(type))
            if propagationStatus:
                query = query.filter(ActionItems.propagation_status == Status(propagationStatus))

            result: Tuple[ActionItems] = (
                query.offset(start)
                .limit(size)
                .all()
            )
            action_items: List = []
            # Format the result
            for action_item in result:
                item = {
                    "id": action_item.id,
                    "type": str(action_item.action_type).strip("'"),
                    "comments": action_item.comments,
                    "propagationStatus": str(action_item.propagation_status).strip("'"),
                    "originatingService": {
                        "name": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.name,
                        "guid": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.guid,
                        "affectedEndpoint": {
                            "id": action_item.affected_client.affected_endpoint.id,
                            "url": action_item.affected_client.affected_endpoint.endpoint.endpoint_url,
                            "method": action_item.affected_client.affected_endpoint.endpoint.method,
                            "changeType": str(action_item.affected_client.affected_endpoint.change_type).strip("'"),
                            "description": action_item.affected_client.affected_endpoint.description,
                            "reason": action_item.affected_client.affected_endpoint.reason,
                            "changeOrigin": str(action_item.affected_client.affected_endpoint.change_origin).strip("'"),
                            "originUniqueID": action_item.affected_client.affected_endpoint.origin_unique_id,
                            "changeOriginURL": action_item.affected_client.affected_endpoint.change_origin_url,
                            "currentSpecification": action_item.affected_client.affected_endpoint.current_specification,
                            "specificationAfterTheChange": action_item.affected_client.affected_endpoint.specification_after_the_change,
                            "status": str(action_item.affected_client.affected_endpoint.status).strip("'"),
                        }
                    },
                    "affectedClient": {
                        "name": action_item.affected_client.client.repo_branch.name,
                        "guid": action_item.affected_client.client.repo_branch.guid,
                    }
                }
                if action_item.meta_data:
                    meta_data = MetaData.model_validate_json(action_item.meta_data)
                
                if action_item.action_type == ActionType.GITHUBPR:
                    item["originatingService"]["githubProject"] = {
                        "repository": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.repository.url,
                        "branch": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.branch,
                        "prId": action_item.affected_client.affected_endpoint.origin_unique_id,
                        "prUrl": action_item.affected_client.affected_endpoint.change_origin_url,
                    }

                    item["affectedClient"]["githubProject"] = {
                        "repository": action_item.affected_client.client.repo_branch.repository.url,
                        "branch": action_item.affected_client.client.repo_branch.branch,
                    }
                    if action_item.meta_data and meta_data.client and meta_data.client.githubProject:
                        item["affectedClient"]["githubProject"]["prId"] = meta_data.client.githubProject.prId
                        item["affectedClient"]["githubProject"]["prUrl"] = meta_data.client.githubProject.prUrl
                        
                elif action_item.action_type == ActionType.JIRATICKET:
                    item["originatingService"]["jiraProject"] = {
                        "url": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.jira_instance_url,
                        "id": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.jira_project_key,
                        "ticketId": action_item.affected_client.affected_endpoint.origin_unique_id,
                        "ticketUrl": action_item.affected_client.affected_endpoint.change_origin_url,
                    }

                    item["affectedClient"]["jiraProject"] = {
                        "url": action_item.affected_client.client.repo_branch.jira_instance_url,
                        "id": action_item.affected_client.client.repo_branch.jira_project_key,
                    }
                    if action_item.meta_data and meta_data.client and meta_data.client.jiraProject:
                        item["affectedClient"]["jiraProject"]["ticketId"] = meta_data.client.jiraProject.ticketId
                        item["affectedClient"]["jiraProject"]["ticketUrl"] = meta_data.client.jiraProject.ticketUrl
                action_items.append(item)
            return action_items
        finally:
            db.close()


@action_item_mutation.field("updateActionItem")
# updateActionItem(id: ID!, comments: String, affected_client: AffectedClient, propagationStatus: String) ActionItem!
def resolve_update_action_item(_, info, id: int, comments: str = None, affected_client: AffectedClient = None, propagationStatus: str = None):
    with SessionLocal() as db:
        try:
            # get the endpoint using url and method.
            action_item = db.query(ActionItems).filter(ActionItems.id == id).first()
            if not action_item:
                raise Exception("Action Item not found")
            if comments:
                if not action_item.comments:
                    action_item.comments = ""
                action_item.comments += datetime.now().strftime(format="%Y-%m-%d %H:%M:%S") + " : " + comments + "\n"
            if propagationStatus:
                action_item.propagation_status = Status(propagationStatus)
            
            meta_data = MetaData()
            if affected_client:
                aff_client = AffectedClient.model_validate(affected_client)
                if action_item.meta_data:
                    meta_data = MetaData.model_validate(action_item.meta_data)

                if aff_client.githubProject:
                    if not meta_data.client:
                        meta_data.client = AffectedClient()
                    meta_data.client.githubProject = GithubProject(prId=aff_client.githubProject.prId, prUrl=aff_client.githubProject.prUrl)
                
                if aff_client.jiraProject:
                    if not meta_data.client:
                        meta_data.client = AffectedClient()
                    meta_data.client.jiraProject = JiraProject(ticketId=aff_client.jiraProject.ticketId, ticketUrl=aff_client.jiraProject.ticketUrl)

            action_item.meta_data = meta_data.model_dump_json()
            db.add(action_item)
            db.commit()
            return action_item.id
        
        finally:
            db.close()

queries.append(action_item_query)
mutations.append(action_item_mutation)