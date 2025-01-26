from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL

from central_system.services import queries, mutations


def custom_error_formatter(error, debug):
    return {
        "message": error.message,
    }


# Load Schema from disk
schema_str = load_schema_from_path(
    "/Users/sakthivelganesan/Desktop/Workspace/MTech/Semester4/Dissertation/Implementation/ADAPT/ADAPT/central_system/services/schema/schema.gql"
)

# # Create executable schema
schema = make_executable_schema(schema_str, queries, mutations)

app = GraphQL(schema, debug=True, error_formatter=custom_error_formatter)
