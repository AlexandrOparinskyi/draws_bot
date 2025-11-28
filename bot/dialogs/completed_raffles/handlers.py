from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select

from bot.states import UserState, CompletedRaffleState


async def back_to_user_home(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=UserState.home,
                               mode=StartMode.RESET_STACK)


async def completed_raffle(callback: CallbackQuery,
                           widget: Select,
                           dialog_manager: DialogManager,
                           item_id: str):
    dialog_manager.dialog_data.update(raffle_id=item_id)

    await dialog_manager.switch_to(state=CompletedRaffleState.raffle)


async def back_to_raffles(callback: CallbackQuery,
                          button: Button,
                          dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=CompletedRaffleState.home)
