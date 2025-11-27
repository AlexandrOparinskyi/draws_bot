from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select

from bot.states import UserState, ActiveRaffleState
from bot.utils import completed_raffle


async def back_to_user_home(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=UserState.home,
                               mode=StartMode.RESET_STACK)


async def active_raffle_select_raffle(callback: CallbackQuery,
                                      widget: Select,
                                      dialog_manager: DialogManager,
                                      item_id: str) -> None:
    dialog_manager.dialog_data.update(raffle_id=item_id)

    await dialog_manager.switch_to(state=ActiveRaffleState.raffle)


async def active_raffle_back_to_home(callback: CallbackQuery,
                                     button: Button,
                                     dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=ActiveRaffleState.home)


async def active_raffle_confirm_finish(callback: CallbackQuery,
                                       button: Button,
                                       dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=ActiveRaffleState.finish_confirm)


async def active_raffle_back_to_raffle(callback: CallbackQuery,
                                       button: Button,
                                       dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(state=ActiveRaffleState.raffle)


async def active_raffle_finish(callback: CallbackQuery,
                               button: Button,
                               dialog_manager: DialogManager) -> None:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    bot = dialog_manager.middleware_data.get("bot")
    sender_bot = dialog_manager.middleware_data.get("sender_bot")

    await completed_raffle(raffle_id, bot, sender_bot)
