import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"{name} environment variable is not set")

    return value


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=get_required_env("DB_USER"),
    password=get_required_env("DB_PASSWORD"),
    host=get_required_env("DB_HOST"),
    port=int(get_required_env("DB_PORT")),
    database=get_required_env("DB_NAME"),
)


engine = create_engine(
    database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass