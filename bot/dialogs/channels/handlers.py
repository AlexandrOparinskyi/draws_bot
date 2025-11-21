from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import UserState, ChannelState


async def channel_back_to_home_menu(callback: CallbackQuery,
                                    button: Button,
                                    dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=UserState.home)


async def channel_back_to_channels(callback: CallbackQuery,
                                   button: Button,
                                   dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=ChannelState.home)


async def channel_instruction(callback: CallbackQuery,
                              button: Button,
                              dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=ChannelState.instruction)
