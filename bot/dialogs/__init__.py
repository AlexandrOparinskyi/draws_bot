from aiogram import Router

from .channels import register_channel_dialogs
from .created_raffles import register_created_raffles_dialogs
from .edit_raffles import register_edit_raffle_dialogs
from .raffles import register_raffle_dialogs
from .user import register_user_dialogs


def register_dialogs(router: Router):
    register_user_dialogs(router)
    register_raffle_dialogs(router)
    register_created_raffles_dialogs(router)
    register_edit_raffle_dialogs(router)
    register_channel_dialogs(router)
