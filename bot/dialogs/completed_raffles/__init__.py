from aiogram import Router
from .dialogs import completed_raffle_dialog


def register_completed_raffle_dialogs(router: Router):
    router.include_router(completed_raffle_dialog)
