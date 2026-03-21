from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()
db_uri = settings.SQLALCHEMY_DATABASE_URI

connect_args = {}
if db_uri.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_uri,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

# Enable WAL mode for SQLite (better concurrent read performance)
if db_uri.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
