from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select, ManagedCheckbox

from bot.states import UserState, CreatedRaffleState, ChangeRaffleState
from bot.utils import delete_raffle_by_id, toggle_ref_system


async def created_raffle_back_to_start(callback: CallbackQuery,
                                       button: Button,
                                       dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=UserState.home,
                               mode=StartMode.RESET_STACK)


async def created_raffle_select_raffle(callback: CallbackQuery,
                                       widget: Select,
                                       dialog_manager: DialogManager,
                                       item_id: str) -> None:
    dialog_manager.dialog_data.update(raffle_id=item_id)

    await dialog_manager.switch_to(state=CreatedRaffleState.raffle)


async def created_raffle_back_to_select(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    await dialog_manager.start(state=CreatedRaffleState.home)


async def created_raffle_delete_raffle(callback: CallbackQuery,
                                       button: Button,
                                       dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=CreatedRaffleState.confirm_delete)


async def created_raffle_delete_yes(callback: CallbackQuery,
                                    button: Button,
                                    dialog_manager: DialogManager) -> None:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    await delete_raffle_by_id(raffle_id)

    await dialog_manager.switch_to(state=CreatedRaffleState.home)


async def created_raffle_back_to_raffle(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    await dialog_manager.switch_to(state=CreatedRaffleState.raffle)


async def created_raffle_preview(callback: CallbackQuery,
                                 button: Button,
                                 dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=CreatedRaffleState.preview)


async def created_raffle_preview_link(callback: CallbackQuery,
                                      button: Button,
                                      dialog_manager: DialogManager) -> None:
    i18n = dialog_manager.middleware_data.get("i18n")

    await callback.answer(
        text=i18n.created.raffle.preview.link(),
        show_alert=True
    )


async def created_raffle_changes(callback: CallbackQuery,
                                 button: Button,
                                 dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=ChangeRaffleState.changes,
                               data=dialog_manager.dialog_data)
