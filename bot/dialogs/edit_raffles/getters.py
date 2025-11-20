from datetime import timedelta, datetime

from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from fluentogram import TranslatorHub

from bot.utils import get_raffle_by_id
from config import MAX_RAFFLE_TITLE_LENGTH, MAX_RAFFLE_DESCRIPTION_LENGTH


async def getter_edit_raffle_changes(i18n: TranslatorHub,
                                        dialog_manager: DialogManager,
                                        **kwargs) -> dict[str, str | None]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)

    text = i18n.created.raffle.changes.text(
        title=raffle.title,
        description=raffle.description,
        end_date=raffle.end_date.strftime("%d.%m.%Y %H:%M"),
        winners_count=raffle.winners_count,
        ref_system="✅ Включена" if raffle.ref_system else "❌ Выключена",
    )
    media = None
    if raffle.photo_id:
        media = MediaAttachment(ContentType.PHOTO, raffle.photo_id)
    if raffle.video_id:
        media = MediaAttachment(ContentType.VIDEO, raffle.video_id)
    edit_buttons = ((i18n.change.title.button(), "title"),
                    (i18n.change.description.button(), "description"),
                    (i18n.change.media.button(), "media"),
                    (i18n.change.end.date.button(), "end_date"),
                    (i18n.change.winners.count.button(), "winners_count"))

    return {"changes_text": text,
            "media": media,
            "edit_buttons": edit_buttons,
            "back_button": i18n.back.button(),
            "ref_system_button": i18n.change.ref.system.button()}


async def getter_edit_raffle_change_param(i18n: TranslatorHub,
                                          dialog_manager: DialogManager,
                                          **kwargs) -> dict[str, str | list]:
    change_param = dialog_manager.dialog_data.get("change_param")
    current_date = datetime.now() + timedelta(hours=3)
    text_data = {
        "title": i18n.change.title.text(
            max_symbols=str(MAX_RAFFLE_TITLE_LENGTH)
        ),
        "description": i18n.change.description.text(
            max_symbols=str(MAX_RAFFLE_DESCRIPTION_LENGTH)
        ),
        "media": i18n.change.media.text(),
        "end_date": i18n.change.end.date.text(
            current_date=current_date.strftime("%d.%m.%Y %H:%M")
        ),
        "winners_count": i18n.change.winners.count.text()
    }

    if change_param == "winners_count":
        buttons = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (10, 10)]
    elif change_param == "media":
        buttons = [(i18n.change.clear.media.button(), "delete_media")]
    else:
        buttons = []

    return {"changed_text": text_data.get(change_param),
            "back_button": i18n.back.button(),
            "buttons": buttons}
