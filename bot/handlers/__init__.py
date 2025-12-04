from aiogram import Router

from .admin import admin_router
from .channels import channel_router
from .start import start_router


def register_handlers(router: Router):
    router.include_router(start_router)
    router.include_router(channel_router)
    router.include_router(admin_router)
