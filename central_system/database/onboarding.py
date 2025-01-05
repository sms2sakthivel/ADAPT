from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import datetime

# Create a base class for your models
Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    modified_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )


# Define the Project model
class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    repository_url = Column(String, unique=True, nullable=False)


# Define Service Model
class Service(Base, TimestampMixin):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    port = Column(Integer, nullable=False)
    branch = Column(String, nullable=False)
    # make project_id and branch as unique constraint
    __table_args__ = (UniqueConstraint("project_id", "branch"),)


# Define Client model
class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    branch = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint("project_id", "branch"),)


# Define Endpoints Model
class Endpoints(Base, TimestampMixin):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    endpoint_url = Column(String, nullable=False)
    method = Column(String, nullable=False)
    description = Column(String, nullable=False)
    specifications = Column(String)
    __table_args__ = (UniqueConstraint("service_id", "endpoint_url", "method"),)


# Define Authentication Protocol
class AuthenticationProtocol(Base, TimestampMixin):
    __tablename__ = "authentication_protocols"
    id = Column(Integer, primary_key=True)
    protocol = Column(String(255), nullable=False)
    specification = Column(String, nullable=False)


# Define Communication Protocol
class CommunicationProtocol(Base, TimestampMixin):
    __tablename__ = "communication_protocols"
    id = Column(Integer, primary_key=True)
    protocol = Column(String(255), nullable=False)


# Define Endpoint Consumers Model
class EndpointConsumers(Base, TimestampMixin):
    __tablename__ = "endpoint_consumers"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    # authentication_protocol_id = Column(Integer, ForeignKey('authentication_protocols.id'))
    # communication_protocol_id = Column(Integer, ForeignKey('communication_protocols.id'))


# Define Endpoint Authentication protocols Map Model
class EndpointAuthenticationProtocolMap(Base, TimestampMixin):
    __tablename__ = "endpoint_authentication_protocol_map"
    id = Column(Integer, primary_key=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    authentication_protocol_id = Column(
        Integer, ForeignKey("authentication_protocols.id")
    )


# Define Service - Communication Protocol Map model
class ServiceCommunicationProtocolMap(Base, TimestampMixin):
    __tablename__ = "service_communication_protocol_map"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    communication_protocol_id = Column(
        Integer, ForeignKey("communication_protocols.id")
    )
