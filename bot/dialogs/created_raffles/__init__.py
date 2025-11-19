from aiogram import Router
from .dialogs import created_raffles_dialog


def register_created_raffles_dialogs(router: Router):
    router.include_router(created_raffles_dialog)
