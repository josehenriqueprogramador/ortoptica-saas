from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

# Resgata a URL do banco do ambiente (definida no docker-compose como sqlite+aiosqlite:///app/ortoptica.db)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///app/ortoptica.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
