from typing import List
from ariadne import QueryType
from central_system.services import queries
from central_system.database import SessionLocal

from central_system.database.onboarding import (
    Endpoints,
)

endpoint_query = QueryType()

@endpoint_query.field("endpoint")
def resolve_endpoint(_, info,url: str, method: str):
    print(f"url : {url}, method: {method}")
    result : List[Endpoints] = []
    with SessionLocal() as db:
        try:
            if method:
                result = (
                    db.query(Endpoints).filter(Endpoints.endpoint_url == url, Endpoints.method == method.upper()).all()
                )
            else:
                result = (
                    db.query(Endpoints).filter(Endpoints.endpoint_url == url).all()
                )
            print(result)
            if not result:
                return None

            # Format the result
            return [
                {
                    "id": endpoint.id,
                    "url": endpoint.endpoint_url,
                    "method": endpoint.method,
                    "description": endpoint.description,
                    "specification": endpoint.specifications,
                }
                for endpoint in result
            ]
        finally:
            db.close()

queries.append(endpoint_query)