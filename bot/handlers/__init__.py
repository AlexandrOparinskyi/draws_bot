from aiogram import Router

from .start import start_router


def register_handlers(router: Router):
    router.include_router(start_router)
