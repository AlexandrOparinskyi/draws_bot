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

    # Кто добавил бота - это ключевое изменение!
    added_by_user = event.from_user  # Тот, кто добавил бота
    if not added_by_user:
        logger.error("No from_user in event")
        return

    added_by_id = added_by_user.id

    try:
        # Получаем права бота из события
        bot_member = event.new_chat_member
        can_post = getattr(bot_member, "can_post_messages", False)
        can_edit = getattr(bot_member, 'can_edit_messages', False)
        can_delete = getattr(bot_member, 'can_delete_messages', False)

        # Логируем информацию
        logger.info(f"Bot added by: {added_by_user.full_name} (ID: {added_by_id})")
        logger.info(f"Bot permissions - post: {can_post}, edit: {can_edit}, delete: {can_delete}")

        if chat.type == "channel":
            # Отправляем сообщение ТОМУ, КТО ДОБАВИЛ бота
            try:
                await bot.send_message(
                    chat_id=added_by_id,
                    text=i18n.completed.add.channel(
                        title=chat.title,
                        can_post="✅" if can_post else "❌",
                        can_edit="✅" if can_edit else "❌",
                        added_by_name=added_by_user.full_name
                    )
                )
                logger.info(f"Notification sent to {added_by_user.full_name} about channel {chat.title}")
            except Exception as msg_err:
                logger.error(f"Error sending message to {added_by_user.full_name}: {msg_err}")
                # Пробуем отправить в чат, если есть username
                if chat.username:
                    try:
                        await bot.send_message(
                            chat_id=chat.id,
                            text=f"@{added_by_user.username}, я добавлен в канал! Проверьте свои права доступа."
                        )
                    except:
                        pass

            # Сохраняем в базу данных
            await create_channel(
                title=chat.title,
                chat_id=chat.id,
                username=chat.username,
                user_id=added_by_id,
                c_type=ChatTypeEnum.CHANNEL,
                can_post=can_post,
                can_edit=can_edit
            )

        else:
            # Для групп/супергрупп
            print(bot_member.__dict__)
            can_post = True
            can_edit = True
            try:
                await bot.send_message(
                    chat_id=added_by_id,
                    text=i18n.completed.add.group(
                        title=chat.title,
                        added_by_name=added_by_user.full_name
                    )
                )
                logger.info(f"Notification sent to {added_by_user.full_name} about group {chat.title}")
            except Exception as msg_err:
                logger.error(f"Error sending message to {added_by_user.full_name}: {msg_err}")

            await create_channel(
                title=chat.title,
                chat_id=chat.id,
                username=chat.username,
                user_id=added_by_id,
                c_type=ChatTypeEnum.SUPERGROUP,
                can_post=can_post,
                can_edit=can_edit
            )

        logger.info(f"Successfully added {chat.type}: {chat.title} (ID: {chat.id}) by {added_by_user.full_name}")

    except Exception as err:
        logger.error(f"Error in handle_bot_added: {err}", exc_info=True)


async def handle_bot_removed(event: ChatMemberUpdated, bot: Bot, i18n: TranslatorHub):
    """Обработка удаления бота из администраторов"""
    chat = event.chat
    removed_by_user = event.from_user  # Кто удалил бота

    try:
        channel = await get_channel_by_chat_id(chat.id)
        if not channel:
            logger.info(f"Channel {chat.title} not found in DB")
            return

        # Отправляем уведомление тому, кто регистрировал канал (user_id в базе)
        if channel.user_id:
            try:
                if channel.type == ChatTypeEnum.CHANNEL:
                    message_text = i18n.deleted.channel(
                        title=chat.title,
                        removed_by_name=removed_by_user.full_name if removed_by_user else "неизвестно"
                    )
                else:
                    message_text = i18n.deleted.group(
                        title=chat.title,
                        removed_by_name=removed_by_user.full_name if removed_by_user else "неизвестно"
                    )

                await bot.send_message(
                    chat_id=int(channel.user_id),
                    text=message_text
                )
                logger.info(f"Delete notification sent to {channel.user_id} about {chat.title}")
            except Exception as err:
                logger.error(f"Error sending delete notification: {err}")

        # Удаляем из базы данных
        await delete_channel_by_chat_id(chat.id)
        logger.info(f"Channel {chat.title} removed from DB")

    except Exception as err:
        logger.error(f"Error in handle_bot_removed: {err}", exc_info=True)