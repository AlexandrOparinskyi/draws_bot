from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import RaffleState


async def user_create_raffle(callback: CallbackQuery,
                             button: Button,
                             dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=RaffleState.title)
