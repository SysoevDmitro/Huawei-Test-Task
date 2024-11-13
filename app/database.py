from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Підключення до бази даних
database = databases.Database(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)

# Налаштування сесії
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()
