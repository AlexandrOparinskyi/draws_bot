import logging
from typing import Optional

from sqlalchemy import insert, select, and_
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session, RafflePlayer

logger = logging.getLogger(__name__)


async def get_raffle_player(user_id: int,
                            raffle_id: int) -> Optional[RafflePlayer]:
    """Get a raffle player"""
    async with get_async_session() as session:
        try:
            return await session.scalar(select(RafflePlayer).where(
                and_(RafflePlayer.user_id == user_id,
                     RafflePlayer.raffle_id == raffle_id)
            ))
        except SQLAlchemyError as err:
            logger.error(f"Database error get new raffle player with id "
                         f"{user_id} and raffle id {raffle_id}: {err}")


async def create_raffle_player(user_id: int,
                               raffle_id: int) -> None:
    """Create a new raffle player"""
    async with get_async_session() as session:
        try:
            await session.execute(insert(RafflePlayer).values(
                user_id=user_id,
                raffle_id=raffle_id
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error create a new raffle player: {err}")
