import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(
    DATABASE_URL,
    echo=True
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )