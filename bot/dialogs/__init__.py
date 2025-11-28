from aiogram import Router

from .avtive_raffles import register_active_raffle_dialogs
from .channels import register_channel_dialogs
from .completed_raffles import register_completed_raffle_dialogs
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
    register_active_raffle_dialogs(router)
    register_completed_raffle_dialogs(router)
