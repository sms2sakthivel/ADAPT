import streamlit as st

from central_system.database import SessionLocal
from central_system.database.onboarding import Service, AffectedClients, Status, ActionItems, ActionType
from central_system.services.model import MetaData

def get_servers():
    with SessionLocal() as db:
        try:
            result = db.query(Service).all()
            services = []
            for service in result:
                service_data = {
                    "port": service.port,
                    "name": service.repo_branch.name,
                    "jira_project": service.repo_branch.jira_project_key,
                    "github_repo": service.repo_branch.repository.url,
                    "endpoints": [],
                }
                for endpoint in service.endpoints:
                    endpoint_data = {
                        "url": endpoint.endpoint_url,
                        "method": endpoint.method,
                        "description": endpoint.description,
                        "clients": []
                    }
                    if endpoint.consumers:
                        for consumer in endpoint.consumers:
                            client = {
                                "name": consumer.client.repo_branch.name,
                                "jira_project": consumer.client.repo_branch.jira_project_key,
                                "github_repo": consumer.client.repo_branch.repository.url,
                                "health": "healthy",
                            }
                            affected_client = db.query(AffectedClients).filter(AffectedClients.client_id == consumer.client_id).first()
                            if affected_client:
                                action_items = db.query(ActionItems).filter(ActionItems.affected_client_id == affected_client.id, ActionItems.propagation_status == Status.INPROGRESS).all()
                                if action_items:
                                    client["actions"] = []
                                for action_item in action_items:
                                    print(action_item.to_dict())
                                    action = {
                                        "platform" : "NA",
                                        "id": "NA",
                                        "url": "NA"
                                    }
                                    meta_data: MetaData = MetaData()
                                    if action_item.meta_data:
                                        meta_data = MetaData.model_validate_json(action_item.meta_data)
                                    if action_item.action_type == ActionType.JIRATICKET:
                                        action["platform"] = "JIRA"
                                        if meta_data and meta_data.client and meta_data.client.jiraProject:
                                                action["id"] = meta_data.client.jiraProject.ticketId
                                                action["url"] = meta_data.client.jiraProject.ticketUrl
                                    elif action_item.action_type == ActionType.GITHUBPR:
                                        action["platform"] = "Github"
                                        if meta_data and meta_data.client and meta_data.client.githubProject:
                                                action["id"] = meta_data and meta_data.client and meta_data.client.githubProject.prId
                                                action["url"] = meta_data.client and meta_data.client.githubProject.prUrl
                                    client["actions"].append(action)
                                print(action_items)
                                if affected_client.healing_status != Status.COMPLETED and len(action_items) > 0:
                                    if str(affected_client.affected_endpoint.change_origin).strip("'") == "jiraticket":
                                        client["health"] = "Possible Future Degradation"
                                        client["origination"] = {
                                            "platform" : "JIRA",
                                            "id": affected_client.affected_endpoint.origin_unique_id,
                                            "url" : f"http://localhost:8080/browse/{affected_client.affected_endpoint.origin_unique_id}",
                                        }
                                    elif str(affected_client.affected_endpoint.change_origin).strip("'") == "githubpr":
                                        client["health"] = "Degraded"
                                        client["origination"] = {
                                            "platform" : "Github",
                                            "id": affected_client.affected_endpoint.origin_unique_id,
                                            "url" : affected_client.affected_endpoint.change_origin_url,
                                        }
                            endpoint_data["clients"].append(client)
                    service_data["endpoints"].append(endpoint_data)
                services.append(service_data)
            return services
        except Exception as e:
            print(e)
        finally:
            db.close()


def get_server(servers: list, name: str):
    for server in servers:
        if server["name"] == name:
            return server
    return None


st.set_page_config(page_title="ADAPT Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("Autonomous Change Detection and Propagation Framework and Toolkit (ADAPT)")

# st.markdown("<h1 style='text-align: center;'>Server Monitoring Dashboard</h1>", unsafe_allow_html=True)
# Dashboard Title
st.markdown("""
    <div style="
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        background-color: #007BFF;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    ">
        Server Monitoring Dashboard
    </div>
""", unsafe_allow_html=True)

# Mock server data
servers = get_servers()
print(f"Servers: \n {servers}")
if servers:
    # Maintain selected server using session state
    if "selected_server" not in st.session_state and servers:
        st.session_state.selected_server = servers[0]["name"]

    # Three-column layout
    col1, col2, col3 = st.columns([1, 1.5, 1.5])

    # Server Selection Panel (Left)
    with col1:
        st.markdown("""
        <div style="
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 3px solid #007BFF;
            margin-bottom: 30px;
            box-shadow: 0px 4px 2px -2px rgba(0,0,0,0.1);
        ">
            Servers
        </div>
    """, unsafe_allow_html=True)

        for server in servers:
            if server['name'] == st.session_state.selected_server:
                st.markdown(
                    f"""
                    <button style="background-color:#007BFF; color:white; padding:10px; 
                    border:none; width:100%; border-radius:5px; cursor:pointer; font-size:16px;">
                    ✅ {server['name']}
                    </button>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if st.button(f" {server['name']}", type="secondary"):
                    st.session_state.selected_server = server["name"]
                    st.rerun()

    # Get selected server
    selected_server = st.session_state.selected_server
    server = get_server(servers=servers, name=selected_server)

    if server:
    # Server Details Panel (Center)
        with col2:
            st.markdown("""
                <div style="
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    padding: 10px;
                    border-bottom: 3px solid #007BFF;
                    margin-bottom: 30px;
                    box-shadow: 0px 4px 2px -2px rgba(0,0,0,0.1);
                ">
                    Server Details
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                padding: 15px;
                border-radius: 10px;
                border-left: 5px solid #007BFF;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            ">
                <p><b>🔹 Name:</b> {server['name']}</p>
                <p><b>🔹 Port:</b> {server['port']}</p>
                <p><b>🔹 JIRA Project:</b> <a href='http://localhost:8080/browse/{server["jira_project"]}' target="_blank">{server['jira_project']}</a></p>
                <p><b>🔹 GitHub Project:</b> <a href='https://github.com/{server["github_repo"]}' target="_blank">{server["github_repo"]}</a></p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4 style='text-align: center;'>Exposed Endpoints</h4>", unsafe_allow_html=True)
            for endpoint in server["endpoints"]:
                st.markdown(f"""
                <div style="
                    background-color: #ffffff;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    border-left: 5px solid #007BFF;
                    box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
                ">
                    <p><b>🔹 {endpoint['method']} {endpoint['url']}</b></p>
                    <p style="margin-left: 20px; color: #555;">{endpoint['description']}</p>
                </div>
                """, unsafe_allow_html=True)

        # Clients Panel (Right)
        with col3:
            st.markdown("""
                <div style="
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                    padding: 10px;
                    border-bottom: 3px solid #007BFF;
                    margin-bottom: 30px;
                    box-shadow: 0px 4px 2px -2px rgba(0,0,0,0.1);
                ">
                    Dependent Clients
                </div>
            """, unsafe_allow_html=True)

            for endpoint in server["endpoints"]:
                for client in endpoint["clients"]:
                    st.markdown(f"""
                    <div style="
                        font-size: 18px;
                        font-weight: bold;
                        color: white;
                        background-color: #007BFF;
                        padding: 8px 15px;
                        border-radius: 5px;
                        margin-top: 15px;
                        text-align: center;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                    ">
                        {client['name']}
                    </div>
                """, unsafe_allow_html=True)
                    with st.expander(f"📌 **{client['name']}**", expanded=True):
                        health_status = "✅ Healthy" if client['health'] == "healthy" else f"⚠️ {client['health']}"
                        if health_status == "✅ Healthy":
                            st.markdown(f"""
                            <div style="
                                background-color: #f8f9fa;
                                padding: 12px;
                                border-radius: 8px;
                                margin-bottom: 10px;
                                border-left: 5px solid {'#28a745' if client['health'] == 'healthy' else '#ffc107'};
                                box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
                            ">
                                <p><b>Name:</b> {client['name']}</p>
                                <p><b>JIRA Project:</b> <a href='http://localhost:8080/browse/{client["jira_project"]}' target="_blank">{client['jira_project']}</a></p>
                                <p><b>GitHub Project:</b> <a href='https://github.com/{client["github_repo"]}' target="_blank">{client["github_repo"]}</a></p>
                                <p><b>Health:</b> {health_status}</p>
                                <p><b>Using Endpoint:</b></p>
                                <p style="margin-left: 20px;"><b>🔹 {endpoint['method']} {endpoint['url']}<b></p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            if "origination" in client:
                                platform = client["origination"].get("platform", "Unknown")
                                issue_id = client["origination"].get("id", "Unknown")
                                issue_url = client["origination"].get("url", "#")
                            else:
                                platform, issue_id, issue_url = "Unknown", "Unknown", "#"
                            st.markdown(f"""
                            <div style="
                                background-color: #f8f9fa;
                                padding: 12px;
                                border-radius: 8px;
                                margin-bottom: 10px;
                                border-left: 5px solid {'#28a745' if client['health'] == 'healthy' else '#ffc107'};
                                box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
                            ">
                                <p><b>Name:</b> {client['name']}</p>
                                <p><b>JIRA Project:</b> <a href='http://localhost:8080/browse/{client["jira_project"]}' target="_blank">{client['jira_project']}</a></p>
                                <p><b>GitHub Project:</b> <a href='https://github.com/{client["github_repo"]}' target="_blank">{client["github_repo"]}</a></p>
                                <p><b>Health:</b> {health_status}</p>
                                <p><b>Reference:</b></p>
                                <p style="margin-left: 20px;"><b>Platform:</b> {platform}</p>
                                <p style="margin-left: 20px;"><b>URL:</b> <a href='{issue_url}' target="_blank">{issue_id}</a></p>
                                <p><b>Using Endpoint:</b></p>
                                <p style="margin-left: 20px;"><b>🔹 {endpoint['method']} {endpoint['url']}</b></p>
                            </div>
                            """, unsafe_allow_html=True)
                            # Display Actions with Enhanced Styling
                            if "actions" in client and client["actions"]:
                                st.markdown("""
                                    <div style="
                                        font-size: 20px;
                                        font-weight: bold;
                                        color: white;
                                        background-color: #FF5733;
                                        padding: 10px;
                                        border-radius: 5px;
                                        text-align: center;
                                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                                        margin-top: 15px;
                                    ">
                                        🛠️ Required Actions
                                    </div>
                                """, unsafe_allow_html=True)

                                for action in client["actions"]:
                                    action_platform = action.get("platform", "NA")
                                    action_id = action.get("id", "NA")
                                    action_url = action.get("url", "#")

                                    st.markdown(f"""
                                    <div style="
                                        background-color: #f8f9fa;
                                        padding: 12px;
                                        border-radius: 8px;
                                        margin-bottom: 10px;
                                        border-left: 5px solid #FF5733;
                                        box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
                                    ">
                                        <p><b>Platform:</b> {action_platform}</p>
                                        <p><b>Action ID:</b> <a href='{action_url}' target="_blank">{action_id}</a></p>
                                    </div>
                                    """, unsafe_allow_html=True)
else:
    st.markdown("No Server Found")
# Overall System Status
st.subheader("Overall Risk Assessment")
st.write("🟢 System is stable, no critical issues detected.")