from sqlalchemy import create_engine
from .onboarding import Base


def create_db_engine():
    engine = create_engine("sqlite:///central_system.db")
    return engine


def create_all_tables(engine):
    print("Creating Tables")
    Base.metadata.create_all(engine)
