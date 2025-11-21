from aiogram.types import User
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id


async def getter_channel_home(i18n: TranslatorHub,
                              event_from_user: User,
                              **kwargs) -> dict[str, list]:
    user = await get_user_by_id(event_from_user.id)

    return {"home_text": i18n.channel.home.text(),
            "add_channel_button": i18n.add.channel.button(),
            "channel_buttons": list(user.channels),
            "back_button": i18n.back.button()}
