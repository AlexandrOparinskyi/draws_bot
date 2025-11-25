from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from config import Config
from reg_bot.states import PlayerState
from reg_bot.utils import get_channels_for_subscribe, create_raffle_player


async def check_subscribe(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager) -> None:
    bot: Bot = dialog_manager.middleware_data.get("check_bot")
    config: Config = dialog_manager.middleware_data.get("config")

    if not dialog_manager.dialog_data.get("main_channel"):
        member = await bot.get_chat_member(config.tg_bot.channel,
                                           callback.from_user.id)
        if member.status == "left":
            return
        else:
            dialog_manager.dialog_data.update(main_channel=True)

    unsub_channels = dialog_manager.dialog_data.get("channels")
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    channels = await get_channels_for_subscribe(unsub_channels,
                                                raffle_id)

    for channel in channels:
        member = await bot.get_chat_member(channel,
                                           callback.from_user.id)
        if member.status == "left":
            return

    await create_raffle_player(callback.from_user.id,
                               raffle_id)

    await dialog_manager.switch_to(state=PlayerState.raffle)
