from sqlmodel import SQLModel, create_engine, Session

# SQLite Database Connection
sqlite_file_name = "buddy.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """
    Create all tables defined in SQLModel metadata.
    Should be called on startup.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency for FastAPI routes to get a DB session.
    """
    with Session(engine) as session:
        yield session
