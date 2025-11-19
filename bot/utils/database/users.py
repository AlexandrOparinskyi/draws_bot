import logging
from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError

from database import User, get_async_session

logger = logging.getLogger(__name__)


async def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by id"""
    async with get_async_session() as session:
        try:
            return await session.scalar(select(User).where(
                User.id == user_id
            ))
        except SQLAlchemyError as err:
            logger.error(f"Database error get user by id {user_id}: {err}")


async def create_user(user_id: int,
                      username: Optional[str],
                      first_name: str,
                      last_name: Optional[str],
                      **kwargs) -> None:
    """Create a new user"""
    async with get_async_session() as session:
        try:
            await session.execute(insert(User).values(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error create a new user: {err}")
