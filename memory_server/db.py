import os

from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")


# IMPORTANT
DATABASE_URL = DATABASE_URL.replace(
    "+asyncpg",
    ""
)

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine
)


def init_db():
    Base.metadata.create_all(bind=engine)