import logging
from typing import Optional

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import SQLAlchemyError

from database import ChatTypeEnum, get_async_session, Channel

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
