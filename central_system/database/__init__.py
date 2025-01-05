from .sqlite3db import create_db_engine, create_all_tables
engine = create_db_engine()
create_all_tables(engine)