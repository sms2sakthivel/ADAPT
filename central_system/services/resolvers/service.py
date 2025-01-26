from ariadne import QueryType, MutationType

from central_system.services import queries, mutations
from central_system.database import SessionLocal
from central_system.database.onboarding import Service

service_query = QueryType()
service_mutation = MutationType()
