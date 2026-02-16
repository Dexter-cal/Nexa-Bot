import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from nexa.models.base import Base
from nexa.models.core import User, Session, Task
from nexa.models.extended import Tool, Guardrail, Action, LLMUsage

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nexa.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        # For SQLite, we might need to enable foreign keys
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
