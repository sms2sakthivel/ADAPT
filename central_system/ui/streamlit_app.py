import streamlit as st
import pandas as pd
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def fetch_data():
    # Configure GraphQL endpoint
    transport = RequestsHTTPTransport(url="https://your-graphql-endpoint.com/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Define GraphQL query
    query = gql("""
    query {
        servers {
            id
            name
            healthStatus
            clients {
                id
                name
                healthStatus
            }
        }
    }
    """)
    
    # Execute query
    result = client.execute(query)
    return result.get("servers", [])

def display_dashboard():
    st.set_page_config(page_title="Server Monitoring Dashboard", layout="wide")
    st.title("🚀 Server Monitoring Dashboard")
    
    # Fetch data
    servers = fetch_data()
    
    # Dashboard Layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🌐 Server Overview")
        for server in servers:
            st.markdown(f"**🔹 {server['name']}** ({get_health_badge(server['healthStatus'])})")
            with st.expander("View Clients"):
                for client in server["clients"]:
                    st.write(f"- {client['name']} {get_health_badge(client['healthStatus'])}")
    
    with col2:
        st.subheader("📊 Server Health Summary")
        df = pd.DataFrame(servers)
        df["Clients Count"] = df["clients"].apply(lambda x: len(x))
        df = df[["name", "healthStatus", "Clients Count"]]
        st.dataframe(df, use_container_width=True)

def get_health_badge(status):
    if status.lower() == "healthy":
        return "✅"
    elif status.lower() == "degraded":
        return "⚠️"
    else:
        return "❌"

if __name__ == "__main__":
    display_dashboard()
