from aiogram import Router
from .dialogs import raffle_settings_dialog


def register_raffle_settings_dialogs(router: Router):
    router.include_router(raffle_settings_dialog)
