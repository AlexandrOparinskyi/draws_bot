from aiogram import Router

from .players import register_player_dialogs


def register_dialogs(router: Router):
    register_player_dialogs(router)
