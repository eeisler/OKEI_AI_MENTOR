from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.config import Config
from sqlalchemy.orm import DeclarativeBase

cfg = Config.load()

DATABASE_URL = (
    f"postgresql+asyncpg://{cfg.db_user}:{cfg.db_password}@"
    f"{cfg.db_host}:{cfg.db_port}/{cfg.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session_factory() as session:
        yield session
