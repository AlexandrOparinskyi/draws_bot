from datetime import datetime, timedelta

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select

from bot.states import ChangeRaffleState, CreatedRaffleState
from bot.utils import toggle_ref_system, delete_media_at_raffle_by_id, edit_selected_param
from config import MAX_RAFFLE_TITLE_LENGTH, MAX_RAFFLE_DESCRIPTION_LENGTH


async def edit_raffle_back_to_raffle(callback: CallbackQuery,
                                     button: Button,
                                     dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=CreatedRaffleState.raffle,
                               data=dialog_manager.dialog_data)


async def edit_raffle_toggle_ref_system(callback: CallbackQuery,
                                        button: Button,
                                        dialog_manage: DialogManager) -> None:
    raffle_id = int(dialog_manage.dialog_data.get("raffle_id"))
    raffle = await toggle_ref_system(raffle_id)
    i18n = dialog_manage.middleware_data.get("i18n")
    if raffle.ref_system:
        await callback.answer(
            text=i18n.enable.ref.system()
        )
    else:
        await callback.answer(
            text=i18n.disable.ref.system()
        )


async def edit_raffle_edit_param(callback: CallbackQuery,
                                 widget: Select,
                                 dialog_manager: DialogManager,
                                 item_id: str) -> None:
    dialog_manager.dialog_data.update(change_param=item_id)

    await dialog_manager.switch_to(state=ChangeRaffleState.change_param)


async def edit_raffle_back_to_changes(callback: CallbackQuery,
                                      button: Button,
                                      dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=ChangeRaffleState.changes)


async def edit_raffle_select_param(callback: CallbackQuery,
                                   widget: Select,
                                   dialog_manager: DialogManager,
                                   item_id: str):
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    change_param = dialog_manager.dialog_data.get("change_param")

    if change_param == "media":
        await delete_media_at_raffle_by_id(raffle_id)
    else:
        await edit_selected_param(change_param, int(item_id), raffle_id)

    await dialog_manager.switch_to(state=ChangeRaffleState.changes)


async def edit_raffle_enter_param(message: Message,
                                  widget: MessageInput,
                                  dialog_manager: DialogManager):
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    change_param = dialog_manager.dialog_data.get("change_param")
    i18n = dialog_manager.middleware_data.get("i18n")
    value = None

    if change_param == "title":
        if len(message.text) > MAX_RAFFLE_TITLE_LENGTH:
            await message.answer(
                text=i18n.raffle.title.error.length.text(
                    max_symbols=str(MAX_RAFFLE_TITLE_LENGTH)
                )
            )
            return
        value = message.text
    elif change_param == "description":
        if len(message.text) > MAX_RAFFLE_DESCRIPTION_LENGTH:
            await message.answer(
                text=i18n.raffle.description.error.length.text(
                    max_symbols=str(MAX_RAFFLE_DESCRIPTION_LENGTH)
                )
            )
            return
        value = message.text
    elif change_param == "end_date":
        try:
            if message.text.strftime("%d.%m.%Y %H:%M") < datetime.now():
                await message.answer(
                    text=i18n.raffle.date.error.text()
                )
                return
            value = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        except ValueError:
            current_date = datetime.now() + timedelta(hours=3)
            await message.answer(
                text=i18n.raffle.date.error.format.text(
                    current_date=current_date
                )
            )
    elif change_param == "winners_count":
        try:
            if int(message.text) < 1:
                await message.answer(
                    text=i18n.raffle.winners.error.text()
                )
                return
            value = int(message.text)
        except ValueError:
            await message.answer(
                text=i18n.raffle.winners.error.type.text()
            )
            return

    await edit_selected_param(change_param, value, raffle_id)

    await dialog_manager.switch_to(state=ChangeRaffleState.changes)


async def edit_raffle_enter_media(message: Message,
                                  widget: MessageInput,
                                  dialog_manager: DialogManager):
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    i18n = dialog_manager.middleware_data.get("i18n")
    param = None
    value = None

    if message.photo:
        if len(message.photo) > 1:
            await message.answer(
                text=i18n.raffle.media.too.many.files.text()
            )
        param = "photo_id"
        value = message.photo[0].file_id
    elif message.video:
        param = "video_id"
        value = message.video.file_id

    await edit_selected_param(param, value, raffle_id)

    await dialog_manager.switch_to(state=ChangeRaffleState.changes)
