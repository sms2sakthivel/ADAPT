from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Enum,
    Text,
)
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
import datetime
from enum import Enum as PyEnum
import json


# Create a base class for your models
Base = declarative_base()


class JSONEncodedList(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# Create Enum for different types of Resources in table. I need to have the type of the job in the jobs table
class ResourceType(PyEnum):
    REPOSITORY = "repository"


class OnboardingStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    modified_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    repo_branches = relationship("RepoBranch", back_populates="repository")


class RepoBranch(Base, TimestampMixin):
    __tablename__ = "repo_branches"
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    branch = Column(String, nullable=False)
    included_extensions = Column(JSONEncodedList, nullable=False)
    status = Column(Enum(OnboardingStatus), nullable=False)
    repository = relationship("Repository", back_populates="repo_branches")
    services = relationship("Service", back_populates="repo_branch")
    clients = relationship("Client", back_populates="repo_branch")
    __table_args__ = (UniqueConstraint("repository_id", "branch"),)


# # Define the Project model
# class Project(Base, TimestampMixin):
#     __tablename__ = "projects"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False)
#     repository_url = Column(String, unique=True, nullable=False)


# Define Service Model
class Service(Base, TimestampMixin):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    repo_branches_id = Column(Integer, ForeignKey("repo_branches.id"))
    port = Column(Integer, nullable=False)
    repo_branch = relationship("RepoBranch", back_populates="services")
    endpoints = relationship("Endpoints", back_populates="service")


# Define Client model
class Client(Base, TimestampMixin):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    repo_branches_id = Column(Integer, ForeignKey("repo_branches.id"))
    repo_branch = relationship("RepoBranch", back_populates="clients")
    consumed_endpoints = relationship("EndpointConsumers", back_populates="client")


# Define Endpoints Model
class Endpoints(Base, TimestampMixin):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    endpoint_url = Column(String, nullable=False)
    method = Column(String, nullable=False)
    description = Column(String, nullable=False)
    specifications = Column(String)
    service = relationship("Service", back_populates="endpoints")
    consumers = relationship("EndpointConsumers", back_populates="endpoint")
    __table_args__ = (UniqueConstraint("service_id", "endpoint_url", "method"),)


# # Define Authentication Protocol
# class AuthenticationProtocol(Base, TimestampMixin):
#     __tablename__ = "authentication_protocols"
#     id = Column(Integer, primary_key=True)
#     protocol = Column(String(255), nullable=False)
#     specification = Column(String, nullable=False)


# # Define Communication Protocol
# class CommunicationProtocol(Base, TimestampMixin):
#     __tablename__ = "communication_protocols"
#     id = Column(Integer, primary_key=True)
#     protocol = Column(String(255), nullable=False)


# Define Endpoint Consumers Model
class EndpointConsumers(Base, TimestampMixin):
    __tablename__ = "endpoint_consumers"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    client = relationship("Client", back_populates="consumed_endpoints")
    endpoint = relationship("Endpoints", back_populates="consumers")
    # authentication_protocol_id = Column(Integer, ForeignKey('authentication_protocols.id'))
    # communication_protocol_id = Column(Integer, ForeignKey('communication_protocols.id'))


# # Define Endpoint Authentication protocols Map Model
# class EndpointAuthenticationProtocolMap(Base, TimestampMixin):
#     __tablename__ = "endpoint_authentication_protocol_map"
#     id = Column(Integer, primary_key=True)
#     endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
#     authentication_protocol_id = Column(
#         Integer, ForeignKey("authentication_protocols.id")
#     )


# # Define Service - Communication Protocol Map model
# class ServiceCommunicationProtocolMap(Base, TimestampMixin):
#     __tablename__ = "service_communication_protocol_map"
#     id = Column(Integer, primary_key=True)
#     service_id = Column(Integer, ForeignKey("services.id"))
#     communication_protocol_id = Column(
#         Integer, ForeignKey("communication_protocols.id")
#     )
