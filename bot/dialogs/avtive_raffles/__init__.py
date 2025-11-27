from aiogram import Router
from .dialogs import active_raffle_dialog


def register_active_raffle_dialogs(router: Router) -> None:
    router.include_router(active_raffle_dialog)
