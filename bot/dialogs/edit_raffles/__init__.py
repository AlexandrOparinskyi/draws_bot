from aiogram import Router
from .dialogs import edit_raffle_dialog


def register_edit_raffle_dialogs(router: Router):
    router.include_router(edit_raffle_dialog)
