from aiogram import Router
from .players import players_router


def register_handlers(router: Router) -> None:
    router.include_router(players_router)
