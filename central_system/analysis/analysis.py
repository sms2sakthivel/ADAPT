import time
from sqlalchemy import or_
from central_system.database import SessionLocal
from central_system.database.onboarding import AffectedEndpoints, EndpointConsumers, AffectedClients, ActionItems, Client, ChangeOrigin, Status, ActionType


class AnalysisEngine:
    def __init__(self):
        pass

    def run_demon(self) -> str:
        while True:
            time.sleep(1)
            with SessionLocal() as db:
                try:
                    # Step 1: Identify all the pending and updated affected endpoints
                    affected_endpoints = db.query(AffectedEndpoints).filter(or_(AffectedEndpoints.status == Status.PENDING, AffectedEndpoints.status == Status.UPDATED)).all()
                    for affected_endpoint in affected_endpoints:
                         print(f"Analysing '{affected_endpoint.endpoint.endpoint_url}'")
                        # Step 2: Identify the Clients affected by these endpoint modifications
                         clients = db.query(Client).join(EndpointConsumers, EndpointConsumers.client_id == Client.id).filter(EndpointConsumers.endpoint_id == affected_endpoint.endpoint_id).all()
                         print(len(clients))
                         for client in clients:
                            if affected_endpoint.status == Status.UPDATED:
                                affected_client = db.query(AffectedClients).filter(AffectedClients.client_id == client.id, AffectedClients.affected_endpoint_id == affected_endpoint.id).first()
                                # If there is affected client entry, then update their corresponding action items to updated. otherwise create new action items
                                if affected_client:
                                    db.query(ActionItems).filter(ActionItems.affected_client_id == affected_client.id, ActionItems.propagation_status != Status.COMPLETED).update({ActionItems.propagation_status: Status.UPDATED}, synchronize_session=False)
                                    db.commit()
                                else:
                                    # A hack to allow the the change to be processed in the next if block. Just to avoid code duplication
                                    affected_endpoint.status = Status.PENDING
                            if affected_endpoint.status == Status.PENDING:
                                    # Step 3: Construct and add a affected client data for middle level tracking purpose
                                    affected_client = AffectedClients(client_id =client.id, affected_endpoint_id=affected_endpoint.id, healing_status=Status.PENDING)
                                    db.add(affected_client)
                                    db.commit()
                                    # Step 4: Create Various Action Items for these affected clients.
                                    if affected_endpoint.change_origin == ChangeOrigin.JIRATICKET:
                                        db.add(ActionItems(affected_client_id=affected_client.id, action_type=ActionType.EMAIL, propagation_status=Status.PENDING))
                                        db.add(ActionItems(affected_client_id=affected_client.id, action_type=ActionType.JIRATICKET, propagation_status=Status.PENDING))
                                    elif affected_endpoint.change_origin == ChangeOrigin.GITHUBPR:
                                        # db.add(ActionItems(affected_client_id=affected_client.id, action_type=ActionType.EMAIL, propagation_status=Status.PENDING))
                                        # db.add(ActionItems(affected_client_id=affected_client.id, action_type=ActionType.JIRATICKET, propagation_status=Status.PENDING))
                                        db.add(ActionItems(affected_client_id=affected_client.id, action_type=ActionType.GITHUBPR, propagation_status=Status.PENDING))
                                    db.commit()
                         # Update the affected endpoint with completed Status
                         affected_endpoint.status = Status.COMPLETED
                         db.add(affected_endpoint)
                         db.commit()
                except Exception as e:
                    print(e)
                    db.rollback()
                    continue
                finally:
                    db.close()
