import os
from dotenv import load_dotenv
import streamlit as st
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

load_dotenv("./central_system/.env", override=True)

# Fixed Values
DEFAULT_BRANCH = "master"
DEFAULT_EXTENSIONS = [".go", ".project.json", ".json", ".yaml", ".yml"]

def construct_onboard_repositories(url: str):
    mutation = gql("""
        mutation NotifyAffectedEndpoints($url: String!, $branch: String!, $included_extensions: [String]!) {
            onboardRepository(
                url: $url
                branch: $branch
                included_extensions: $included_extensions
            ) {
                id
            }
        }
    """)

    variables = {
        "url": url,
        "branch": DEFAULT_BRANCH,
        "included_extensions": DEFAULT_EXTENSIONS
    }
    return mutation, variables

st.set_page_config(page_title="Onboarding Service", layout="wide")

# Page Title

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
        Onboard a New Service
    </div>
""", unsafe_allow_html=True)

repo_url = st.text_input("GitHub Repository URL", placeholder="Enter GitHub repo URL", key="repo_url")

# Onboarding Button
st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
if st.button(" Start Onboarding", use_container_width=False):
    if repo_url:
        try:
            service_url = os.environ["SERVICE_URL"]
            url = f"{service_url}/graphql"
            # url = url.replace("http://host.docker.internal", "http://localhost")

            transport = RequestsHTTPTransport(url=url, verify=False)
            client = Client(transport=transport, fetch_schema_from_transport=True)

            query, variables = construct_onboard_repositories(url=repo_url)
            response = client.execute(query, variable_values=variables)

            if "onboardRepository" in response and "id" in response["onboardRepository"]:
                st.success("✅ Onboarding started successfully!")
        except Exception as e:
            error_msg = e.__dict__["errors"][0]["message"] if "errors" in e.__dict__ else str(e)
            st.error(f"❌ Onboarding Failed: **{error_msg}**")
    else:
        st.warning("⚠️ Please enter the GitHub repository URL.")

st.markdown("</div>", unsafe_allow_html=True)  # Close button container