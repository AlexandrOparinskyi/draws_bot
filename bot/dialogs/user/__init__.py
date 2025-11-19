from aiogram import Router
from .dialogs import user_dialog


def register_user_dialogs(router: Router):
    router.include_router(user_dialog)
