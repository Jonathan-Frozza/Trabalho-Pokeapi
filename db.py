import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 🔹 Define URL de conexão
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    if os.getenv("RUNNING_IN_DOCKER") == "true":
        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/pokemondb"
    else:
        # Fallback local (útil para dev)
        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pokemondb"

# 🔹 Engine assíncrono
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# 🔹 Factory de sessões assíncronas
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# 🔹 Base declarativa para os modelos
Base = declarative_base()

# 🔹 Dependency injection (FastAPI)
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
