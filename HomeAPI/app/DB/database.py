from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DB_PATH = Path(__file__).parent.parent / 'task_db.db'
SQLALCHEMY_DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Создаем асинхронный движок
engine = create_async_engine(SQLALCHEMY_DB_URL)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Важно для работы с FastAPI
    autocommit=False,
    autoflush=False, # Не будет сам запрашивать данные
)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all())