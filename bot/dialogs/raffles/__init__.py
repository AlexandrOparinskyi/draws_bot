from aiogram import Router
from .dialogs import raffle_dialog


def register_raffle_dialogs(router: Router):
    router.include_router(raffle_dialog)
