import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

class Base(DeclarativeBase):
    pass

def get_database_name() -> str:
    return os.getenv("DB_NAME", "document_api")

def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "document_api")
    port = os.getenv("DB_PORT", "3306")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

def create_database() -> None:
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    port = os.getenv("DB_PORT", "3306")
    database = get_database_name()

    server_url = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/"
    )

    engine = create_engine(server_url, pool_pre_ping=True)

    with engine.connect() as connection:
        connection.execute(
            text(f"CREATE DATABASE IF NOT EXISTS `{database}`")
        )

    engine.dispose()

@lru_cache(maxsize=1)
def get_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)

@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)

def get_db() -> Session:
    return get_session_factory()()

def init_db() -> None:
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())

def init_db() -> None:

    from app.database import models  # noqa: F401

    Base.metadata.create_all(
        bind=get_engine()
    )
