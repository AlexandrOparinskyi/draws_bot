from datetime import datetime, timedelta

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select, Button

from bot.states import RaffleState, CreatedRaffleState
from bot.utils import create_raffle
from config import MAX_RAFFLE_TITLE_LENGTH, MAX_RAFFLE_DESCRIPTION_LENGTH


async def raffle_error_format(message: Message,
                              widget: MessageInput,
                              dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")
    await message.answer(
        text=i18n.raffle.error.format.text()
    )


async def raffle_enter_title(message: Message,
                             widget: MessageInput,
                             dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")

    if len(message.text) > MAX_RAFFLE_TITLE_LENGTH:
        await message.answer(
            text=i18n.raffle.title.error.length.text(
                max_symbols=MAX_RAFFLE_TITLE_LENGTH
            )
        )
        return

    dialog_manager.dialog_data.update(title=message.text)

    await dialog_manager.switch_to(state=RaffleState.description)


async def raffle_enter_description(message: Message,
                                   widget: MessageInput,
                                   dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")

    if len(message.text) > MAX_RAFFLE_DESCRIPTION_LENGTH:
        await message.answer(
            text=i18n.raffle.description.error.length.text(
                max_symbols=MAX_RAFFLE_DESCRIPTION_LENGTH
            )
        )
        return

    dialog_manager.dialog_data.update(description=message.text)

    await dialog_manager.switch_to(state=RaffleState.media)


async def raffle_load_media(message: Message,
                            widget: MessageInput,
                            dialog_manager: DialogManager) -> None:
    if message.photo:
        dialog_manager.dialog_data.update(photo_id=message.photo[-1].file_id)

    if message.video:
        dialog_manager.dialog_data.update(video_id=message.video.file_id)

    await dialog_manager.switch_to(state=RaffleState.end_date)


async def raffle_skip_load_media(callback: CallbackQuery,
                                 button: Button,
                                 dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=RaffleState.end_date)


async def raffle_enter_end_date(message: Message,
                                widget: MessageInput,
                                dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")

    try:
        m_text = message.text.replace("⁩", "").replace("⁨", "")
        message_date = datetime.strptime(m_text, "%d.%m.%Y %H:%M")
        if message_date > datetime.now():
            dialog_manager.dialog_data.update(end_date=message_date)
            await dialog_manager.switch_to(state=RaffleState.winners_count)
        else:
            await message.answer(
                text=i18n.raffle.date.error.text()
            )
    except ValueError:
        current_date = datetime.now() + timedelta(hours=1)
        await message.answer(
            i18n.raffle.date.error.format.text(
                current_date=current_date.strftime("%d.%m.%Y %H:%M")
            )
        )


async def raffle_enter_winners_count(message: Message,
                                     widget: MessageInput,
                                     dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")

    try:
        if int(message.text) > 0:
            dialog_manager.dialog_data.update(winners_count=message.text)
            await dialog_manager.switch_to(state=RaffleState.ref_system)
        else:
            await message.answer(
                text=i18n.raffle.winners.error.text()
            )
    except ValueError:
        await message.answer(
            text=i18n.raffle.winners.error.type.text()
        )


async def raffle_select_winners_count(callback: CallbackQuery,
                                      widget: Select,
                                      dialog_manager: DialogManager,
                                      item_id: str) -> None:
    dialog_manager.dialog_data.update(winners_count=item_id)

    await dialog_manager.switch_to(state=RaffleState.ref_system)


async def raffle_select_ref_system(callback: CallbackQuery,
                                   button: Button,
                                   dialog_manager: DialogManager):
    if button.widget_id == "enable_ref_system":
        dialog_manager.dialog_data.update(ref_system=True)
    else:
        dialog_manager.dialog_data.update(ref_system=False)

    raffle_id = await create_raffle(user_id=callback.from_user.id,
                                    **dialog_manager.dialog_data)

    await dialog_manager.start(state=CreatedRaffleState.raffle,
                               data={"raffle_id": raffle_id})
