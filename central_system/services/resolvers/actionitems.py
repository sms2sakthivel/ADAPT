import json
from typing import Tuple, List
from ariadne import QueryType
from central_system.services import queries
from central_system.database import SessionLocal

from central_system.database.onboarding import (
    ActionItems,
    ActionType,
)

actionitem_query = QueryType()
@actionitem_query.field("actionItems")
def resolve_repositories(_, info, page=1, size=100):
    with SessionLocal() as db:
        try:
            page = int(page)
            size = int(size)
            start = (page - 1) * size
            result: Tuple[ActionItems] = (
                db.query(ActionItems)
                .offset(start)
                .limit(size)
                .all()
            )
            action_items: List = []
            # Format the result
            for action_item in result:
                item = {
                    "id": action_item.id,
                    "type": action_item.action_type,
                    "comments": action_item.comments,
                    "propagationStatus": action_item.propagation_status,
                    "originatingService": {
                        "name": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.name,
                        "guid": action_item.affected_client.affected_endpoint.endpoint.service.repo_branch.guid,
                        "affectedEndpoint": {
                            "id": action_item.affected_client.affected_endpoint.id,
                            "url": action_item.affected_client.affected_endpoint.endpoint.endpoint_url,
                            "method": action_item.affected_client.affected_endpoint.endpoint.method,
                            "changeType": action_item.affected_client.affected_endpoint.change_type,
                            "description": action_item.affected_client.affected_endpoint.description,
                            "reason": action_item.affected_client.affected_endpoint.reason,
                            "changeOrigin": action_item.affected_client.affected_endpoint.change_origin,
                            "originUniqueID": action_item.affected_client.affected_endpoint.origin_unique_id,
                            "changeOriginURL": action_item.affected_client.affected_endpoint.change_origin_url,
                            "status": action_item.affected_client.affected_endpoint.status,
                        }
                    },
                    "affectedClient": {
                        "name": action_item.affected_client.client.repo_branch.name,
                        "guid": action_item.affected_client.client.repo_branch.guid,
                    }
                }
                if action_item.meta_data:
                    meta_data = json.loads(action_item.meta_data)
                
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
                    if action_item.meta_data:
                        item["affectedClient"]["githubProject"] = {
                            "prId": meta_data["client"]["githubProject"]["pr_id"],
                            "prUrl": meta_data["client"]["githubProject"]["pr_url"]
                        }
                        
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
                    if action_item.meta_data:
                        item["affectedClient"]["jiraProject"] = {
                            "ticketId": meta_data["client"]["jiraProject"]["ticket_id"],
                            "ticketUrl": meta_data["client"]["jiraProject"]["ticket_url"]
                        }
                action_items.append(item)
            return action_items
        finally:
            db.close()

queries.append(actionitem_query)