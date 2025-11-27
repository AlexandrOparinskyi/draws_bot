from datetime import datetime

from aiogram import Bot

from database import Raffle
from . import completed_raffle
from .database import get_active_raffles


async def check_end_time_raffle(bot: Bot, sender_bot: Bot) -> None:
    raffles: list[Raffle] = await get_active_raffles()
    now = datetime.now()

    for raffle in raffles:
        if raffle.end_date <= now:
            await completed_raffle(raffle.id, bot, sender_bot)
