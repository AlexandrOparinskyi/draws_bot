from sqlalchemy import select, and_

from database import Channel, get_async_session, RaffleChannel, Raffle


async def get_channels_for_subscribe(unsub_ch: list[int],
                                     raffle_id: int) -> list[int]:
    """Get channels for subscribe"""
    async with get_async_session() as session:
        result = await session.scalars(select(
            Channel
        ).join(
            RaffleChannel, (Channel.id == RaffleChannel.channel_id)
        ).where(
            and_(RaffleChannel.raffle_id == raffle_id,
                 Channel.chat_id.in_(unsub_ch))
        ))

        return [int(ch.chat_id) for ch in result]
