import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker,
                                    AsyncSession)

from config import load_config, Config

logger = logging.getLogger(__name__)

config: Config = load_config()
DB_HOST = config.db.host
DB_PORT = config.db.port
DB_NAME = config.db.name
DB_USER = config.db.user
DB_PASS = config.db.password

db_url = (f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@"
          f"{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_async_engine(url=db_url, echo=False)
async_session = async_sessionmaker(bind=engine,
                                   expire_on_commit=False,
                                   class_=AsyncSession)


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception as err:
            logger.error(f"Error at database: {err}")
            await session.rollback()
            raise
        finally:
            await session.close()
