from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import (RaffleState,
                        CreatedRaffleState,
                        ChannelState,
                        ActiveRaffleState)


async def user_create_raffle(callback: CallbackQuery,
                             button: Button,
                             dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=RaffleState.title)


async def user_created_raffles(callback: CallbackQuery,
                               button: Button,
                               dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=CreatedRaffleState.home)


async def user_channels(callback: CallbackQuery,
                        button: Button,
                        dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=ChannelState.home)


async def user_active_raffles(callback: CallbackQuery,
                             button: Button,
                             dialog_manager: DialogManager) -> None:
    await dialog_manager.start(state=ActiveRaffleState.home)
