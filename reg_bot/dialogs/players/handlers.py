import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select

from bot.utils import get_raffle_by_id
from config import Config
from reg_bot.states import PlayerState
from reg_bot.utils import get_channels_for_subscribe, create_raffle_player

logger = logging.getLogger(__name__)


async def select_raffle(callback: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str) -> None:
    dialog_manager.dialog_data.update(raffle_id=item_id)

    await dialog_manager.switch_to(state=PlayerState.raffle)


async def back_to_select_raffles(callback: CallbackQuery,
                                 button: Button,
                                 dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=PlayerState.home)


async def check_subscribe(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager) -> None:
    try:
        await callback.answer("🔍 Проверяю подписки...")
    except Exception as e:
        logger.debug(f"Callback answer failed: {e}")

    bot: Bot = dialog_manager.middleware_data.get("check_bot")
    config: Config = dialog_manager.middleware_data.get("config")

    if not dialog_manager.dialog_data.get("main_channel"):
        try:
            member = await bot.get_chat_member(config.tg_bot.channel,
                                               callback.from_user.id)
            if member.status == "left":
                return
            else:
                dialog_manager.dialog_data.update(main_channel=True)
        except TelegramBadRequest as e:
            return

    unsub_channels = dialog_manager.dialog_data.get("channels")
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    channels = await get_channels_for_subscribe(unsub_channels,
                                                raffle_id)

    if channels:
        tasks = []
        for channel in channels:
            task = check_single_channel_safe(bot, channel, callback.from_user.id)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                return
            if not result:
                return

    if dialog_manager.dialog_data.get("ref_parent"):
        await create_raffle_player(
            callback.from_user.id,
            raffle_id,
            int(dialog_manager.dialog_data.get("ref_parent"))
        )
    else:
        await create_raffle_player(callback.from_user.id,
                                   raffle_id)

    await dialog_manager.switch_to(state=PlayerState.raffle)


async def check_single_channel_safe(bot: Bot, channel: int, user_id: int) -> bool:
    """Безопасная проверка подписки на один канал с таймаутом"""
    try:
        # Добавляем таймаут 3 секунды
        member = await asyncio.wait_for(
            bot.get_chat_member(channel, user_id),
            timeout=3.0
        )
        return member.status != "left"
    except TelegramBadRequest as e:
        # Если пользователя нет в канале или канал не найден
        return False
    except asyncio.TimeoutError:
        logger.warning(f"Timeout checking channel {channel}")
        return False
    except Exception as e:
        logger.error(f"Error checking channel {channel}: {e}")
        return False


async def player_invite(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager) -> None:
    bot: Bot = dialog_manager.middleware_data.get("bot")
    config: Config = dialog_manager.middleware_data.get("config")
    i18n = dialog_manager.middleware_data.get("i18n")

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)

    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")

    text = (f"{raffle.description}\n\n"
            f"Заканчивается {date} в {time}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=raffle.title,
                url=f"https://t.me/{config.reg_tg_bot.username}?start="
                    f"{raffle_id}_{callback.from_user.id}"
            )]
        ]
    )
    try:
        if raffle.photo_id:
            await bot.send_photo(callback.from_user.id,
                                 photo=raffle.player_photo_id,
                                 caption=text,
                                 reply_markup=keyboard)
        elif raffle.video_id:
            await bot.send_video(callback.from_user.id,
                                 video=raffle.player_video_id,
                                 caption=text,
                                 reply_markup=keyboard)
        else:
            await bot.send_message(callback.from_user.id,
                                   text=text,
                                   reply_markup=keyboard)
    except Exception as err:
        logger.error(f"Error send mail to user "
                     f"{callback.from_user.id}: {err}")

    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=i18n.back.button(),
                callback_data="back_to_raffle"
            )]
        ]
    )
    await callback.message.answer(
        text=i18n.invite.instruction(),
        reply_markup=back_keyboard
    )
