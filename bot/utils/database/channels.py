import logging
from typing import Optional

from asyncpg import UniqueViolationError
from sqlalchemy import insert, select, delete, case, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import aliased

from database import ChatTypeEnum, get_async_session, Channel, RaffleChannel, RaffleChannelTypeEnum

logger = logging.getLogger(__name__)


async def create_channel(title: Optional[str],
                         chat_id: int,
                         username: Optional[str],
                         user_id: int,
                         c_type: ChatTypeEnum,
                         can_post: bool = True,
                         can_edit: bool = True,
                         **kwargs) -> None:
    """Create a new chat"""
    async with get_async_session() as session:
        try:
            await session.execute(insert(Channel).values(
                title=title,
                chat_id=chat_id,
                username=username,
                user_id=user_id,
                type=c_type,
                can_post=can_post,
                can_edit=can_edit
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error create a channel: {err}")


async def get_channel_by_chat_id(chat_id: int) -> Optional[Channel]:
    """Get channel by chat id"""
    async with get_async_session() as session:
        try:
            return await session.scalar(select(Channel).where(
                Channel.chat_id == chat_id
            ))
        except SQLAlchemyError as err:
            logger.error(f"Database error get channel with id {chat_id}: "
                         f"{err}")


async def delete_channel_by_chat_id(chat_id: int) -> None:
    """Delete a channel by chat id"""
    async with get_async_session() as session:
        try:
            await session.execute(delete(Channel).where(
                Channel.chat_id == chat_id
            ))
            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error delete channel with id {chat_id}: "
                         f"{err}")


async def get_user_active_channels(
        raffle_id: int,
        user_id: int,
        channel_type: RaffleChannelTypeEnum
) -> list:
    async with get_async_session() as session:
        try:
            RaffleChannelAlias = aliased(RaffleChannel)

            stmt = (
                select(
                    Channel.id,
                    Channel.title,
                    case(
                        (and_(RaffleChannelAlias.raffle_id == raffle_id,
                              RaffleChannelAlias.channel_type == channel_type),
                         True),
                        else_=False
                    ).label("is_selected")
                )
                .outerjoin(
                    RaffleChannelAlias,
                    and_(RaffleChannelAlias.channel_id == Channel.id,
                         RaffleChannelAlias.raffle_id == raffle_id,
                         RaffleChannelAlias.channel_type == channel_type)
                )
                .where(
                    and_(Channel.user_id == user_id,
                         Channel.can_post == True,
                         Channel.can_edit == True)
                )
            )

            result = await session.execute(stmt)
            channels = result.all()

            return [
                (
                    f"{'✅' if is_selected else '⬜'} {title}",
                    channel_id,
                    is_selected
                )
                for channel_id, title, is_selected in channels
            ]
        except SQLAlchemyError as err:
            logger.error(f"Database error get channels for "
                         f"raffle {raffle_id} and user {user_id}"
                         f" at channel_type {channel_type}: {err}")


async def toggle_raffle_channel(raffle_id: int,
                                channel_id: int,
                                channel_type: RaffleChannelTypeEnum) -> None:
    """Create or delete raffle channel"""
    async with get_async_session() as session:
        try:
            existing = await session.execute(select(RaffleChannel).where(
                RaffleChannel.raffle_id == raffle_id,
                RaffleChannel.channel_id == channel_id,
                RaffleChannel.channel_type == channel_type
            ))
            existing_channel = existing.scalar_one_or_none()

            if existing_channel is None:
                await session.execute(insert(RaffleChannel).values(
                    raffle_id=raffle_id,
                    channel_id=channel_id,
                    channel_type=channel_type
                ))
            else:
                await session.delete(existing_channel)

            await session.commit()
        except SQLAlchemyError as err:
            logger.error(f"Database error create raffle channel "
                         f"with raffle {raffle_id}, channel "
                         f"{channel_id}: {err}")
