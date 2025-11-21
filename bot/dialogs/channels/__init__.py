from aiogram import Router
from .dialogs import channel_dialog


def register_channel_dialogs(router: Router):
    router.include_routers(channel_dialog)
