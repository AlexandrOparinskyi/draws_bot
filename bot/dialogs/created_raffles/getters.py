from aiogram.enums import ContentType
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id, get_raffle_by_id


async def getter_created_raffle_home(i18n: TranslatorHub,
                                     event_from_user: User,
                                     **kwargs) -> dict[str, str | list]:
    user = await get_user_by_id(event_from_user.id)

    return {"home_text": i18n.created.raffle.home.text(),
            "raffle_buttons": user.created_raffles,
            "back_button": i18n.back.button()}


async def getter_created_raffle_raffle(i18n: TranslatorHub,
                                       dialog_manager: DialogManager,
                                       **kwargs) -> dict[str, str]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")

    text = (f"<b>{raffle.title}</b>\n\n"
            f"{raffle.description}\n\n"
            f"Закончится: <b>{date}</b> в <b>{time}</b>")

    media = None
    if raffle.photo_id:
        media = MediaAttachment(ContentType.PHOTO, raffle.photo_id)
    if raffle.video_id:
        media = MediaAttachment(ContentType.VIDEO, raffle.video_id)

    return {"raffle_text": text,
            "media": media,
            "back_button": i18n.back.button(),
            "edit_button": i18n.edit.button(),
            "subscribe_channels_button": i18n.subscribe.channels.button(),
            "public_channels_button": i18n.public.channels.button(),
            "start_raffle": i18n.start.raffle()}
