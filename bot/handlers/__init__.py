from aiogram import Router

from .channels import channel_router
from .start import start_router


def register_handlers(router: Router):
    router.include_router(start_router)
    router.include_router(channel_router)
