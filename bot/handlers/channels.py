import logging

from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from fluentogram import TranslatorHub

from bot.utils import create_channel, get_channel_by_chat_id, delete_channel_by_chat_id
from database import ChatTypeEnum

channel_router = Router()
logger = logging.getLogger(__name__)


@channel_router.my_chat_member()
async def bot_added_as_admin(event: ChatMemberUpdated,
                             bot: Bot,
                             i18n: TranslatorHub) -> None:
    """Срабатывает когда бота добавляют как администратора"""
    chat = event.chat
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    if old_status == "administrator" and new_status != "administrator":
        await handle_bot_removed(event, bot, i18n)
        return

    if new_status == "administrator" and old_status != "administrator":
        await handle_bot_added(event, bot, i18n)


async def handle_bot_added(event: ChatMemberUpdated, bot: Bot, i18n: TranslatorHub):
    """Обработка добавления бота как администратора"""
    chat = event.chat

    try:
        admins = await bot.get_chat_administrators(chat.id)
        creator_id = None

        for admin in admins:
            if admin.status == "creator":
                creator_id = admin.user.id
                break

        bot_member = event.new_chat_member
        can_post = getattr(bot_member, "can_post_messages", False)
        can_edit = getattr(bot_member, 'can_edit_messages', False)

        if chat.type == "channel":
            try:
                await bot.send_message(
                    chat_id=creator_id,
                    text=i18n.completed.add.channel(
                        title=chat.title,
                        can_post="✅" if can_post else "❌",
                        can_edit="✅" if can_edit else "❌",
                    )
                )
            except Exception as err:
                logger.error(f"Error send message to connect channel: {err}")

            await create_channel(chat.title,
                                 chat.id,
                                 chat.username,
                                 creator_id,
                                 ChatTypeEnum.CHANNEL,
                                 can_post,
                                 can_edit)
        else:
            try:
                await bot.send_message(
                    chat_id=creator_id,
                    text=i18n.completed.add.group(
                        title=chat.title
                    )
                )
            except Exception as err:
                logger.error(f"Error send message to connect channel: {err}")

            await create_channel(chat.title,
                                 chat.id,
                                 chat.username,
                                 creator_id,
                                 ChatTypeEnum.SUPERGROUP)

    except Exception as err:
        logger.error(f"Error in handle_bot_added: {err}")


async def handle_bot_removed(event: ChatMemberUpdated, bot: Bot, i18n: TranslatorHub):
    """Обработка удаления бота из администраторов"""
    chat = event.chat

    try:
        channel = await get_channel_by_chat_id(chat.id)
        if not channel:
            logger.info(f"Channel {chat.title} not found in DB")
            return

        if channel.type == ChatTypeEnum.CHANNEL:
            try:
                await bot.send_message(
                    chat_id=int(channel.user_id),
                    text=i18n.deleted.channel(title=chat.title)
                )
            except Exception as err:
                logger.error(f"Error sending delete notification for channel: {err}")
        else:
            try:
                await bot.send_message(
                    chat_id=int(channel.user_id),
                    text=i18n.deleted.group(title=chat.title)
                )
            except Exception as err:
                logger.error(f"Error sending delete notification for group: {err}")

        await delete_channel_by_chat_id(chat.id)
        logger.info(f"Channel {chat.title} is deleted")

    except Exception as err:
        logger.error(f"Error in handle_bot_removed: {err}")
