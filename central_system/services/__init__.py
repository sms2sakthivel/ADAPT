from typing import List
from ariadne import QueryType, MutationType

queries: List[QueryType] = []
mutations: List[MutationType] = []

from central_system.services.resolvers import repository_query, repository_mutation
