from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import UserState


async def channel_back_to_home_menu(callback: CallbackQuery,
                                    button: Button,
                                    dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=UserState.home)
