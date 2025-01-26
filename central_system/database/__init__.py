from .sqlite3db import create_db_engine, create_all_tables
from sqlalchemy.orm import sessionmaker

engine = create_db_engine()
create_all_tables(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
