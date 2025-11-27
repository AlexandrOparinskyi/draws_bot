import logging

from sqlalchemy import update, and_
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session, RafflePlayer

logger = logging.getLogger(__name__)


async def make_place_to_player(place: int,
                               player_id: int,
                               raffle_id: int) -> None:
    async with get_async_session() as session:
        try:
            await session.execute(update(RafflePlayer).where(
                and_(RafflePlayer.user_id == player_id,
                     RafflePlayer.raffle_id == raffle_id)
            ).values(
                place=place
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error make place to player {player_id}: "
                         f"{err}")
