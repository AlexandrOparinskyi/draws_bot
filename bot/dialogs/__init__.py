from aiogram import Router

from .raffles import register_raffle_dialogs
from .user import register_user_dialogs


def register_dialogs(router: Router):
    register_user_dialogs(router)
    register_raffle_dialogs(router)
