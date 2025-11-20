import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session, Raffle

logger = logging.getLogger(__name__)


async def create_raffle(user_id: int,
                        title: str,
                        description: str,
                        end_date: datetime,
                        winners_count: str,
                        ref_system: bool,
                        photo_id: Optional[str] = None,
                        video_id: Optional[str] = None,
                        **kwargs) -> Optional[int]:
    """Create a new raffle"""
    async with get_async_session() as session:
        try:
            query = await session.execute(insert(Raffle).values(
                user_id=user_id,
                title=title,
                description=description,
                end_date=end_date,
                winners_count=int(winners_count),
                ref_system=ref_system,
                photo_id=photo_id,
                video_id=video_id
            ).returning(Raffle.id))
            await session.commit()
            return query.scalar_one_or_none()
        except SQLAlchemyError as err:
            logger.error(f"Database error create a new raffle: {err}")


async def get_raffle_by_id(raffle_id: int) -> Optional[Raffle]:
    """Get raffle by id. If raffle not found, returning None"""
    async with get_async_session() as session:
        try:
            return await session.scalar(select(Raffle).where(
                Raffle.id == raffle_id
            ))
        except SQLAlchemyError as err:
            logger.error(f"Database error get raffle with id {raffle_id}: "
                         f"{err}")


async def delete_raffle_by_id(raffle_id: int) -> None:
    """Delete raffle by id"""
    async with get_async_session() as session:
        try:
            await session.execute(delete(Raffle).where(
                Raffle.id == raffle_id
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error delete raffle with id {raffle_id}: "
                         f"{err}")
