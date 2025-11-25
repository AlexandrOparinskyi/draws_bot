from aiogram import Router
from .dialogs import player_dialog


def register_player_dialogs(router: Router):
    router.include_router(player_dialog)
