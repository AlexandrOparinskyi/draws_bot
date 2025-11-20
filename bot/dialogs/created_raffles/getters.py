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

    text = i18n.created.raffle.selected.text(
        title=raffle.title,
        end_date=raffle.end_date.strftime("%d.%m.%Y %H:%M"),
        winners_count=raffle.winners_count,
        ref_system="✔️ Включена" if raffle.ref_system else "❌ Выключена",
        subscribe_channels=len(raffle.get_subscribe_channels),
        public_channels=len(raffle.get_public_channels)
    )

    return {"raffle_text": text,
            "back_button": i18n.back.button(),
            "edit_button": i18n.edit.raffle.button(),
            "subscribe_channels_button": i18n.subscribe.channels.button(),
            "public_channels_button": i18n.public.channels.button(),
            "start_raffle": i18n.start.raffle.button(),
            "delete_raffle": i18n.delete.raffle.button(),
            "preview_button": i18n.preview.raffle.button()}


async def getter_create_raffle_confirm_delete(i18n: TranslatorHub,
                                              **kwargs) -> dict[str, str]:
    return {"confirm_delete_text": i18n.created.raffle.confirm.delete.text(),
            "yes_button": i18n.delete.raffle.yes.button(),
            "no_button": i18n.delete.raffle.no.button()}


async def getter_created_raffle_preview(i18n: TranslatorHub,
                                        dialog_manager: DialogManager,
                                        **kwargs) -> dict[str, str]:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")

    button = raffle.title
    text = (f"{raffle.description}\n\n"
            f"Заканчивается {date} в {time}")
    media = None
    if raffle.photo_id:
        media = MediaAttachment(ContentType.PHOTO, raffle.photo_id)
    if raffle.video_id:
        media = MediaAttachment(ContentType.VIDEO, raffle.video_id)

    return {"raffle_text": text,
            "title_button": button,
            "media": media,
            "back_button": i18n.back.button()}
