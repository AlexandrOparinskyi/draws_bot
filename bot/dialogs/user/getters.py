from aiogram.types import User
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id


async def getter_user_home(i18n: TranslatorHub,
                           event_from_user: User,
                           **kwargs) -> dict[str, str]:
    user = await get_user_by_id(event_from_user.id)
    created_raffles_button = i18n.created.raffles.button(
        raffle_count=len(user.created_raffles)
    )
    active_raffles_button = i18n.active.raffles.button(
        raffle_count=len(user.active_raffles)
    )
    completed_raffles_button = i18n.completed.raffles.button(
        raffle_count=len(user.completed_raffles)
    )

    return {"home_text": i18n.user.home.text(),
            "new_raffle_button": i18n.new.raffle.button(),
            "created_raffles_button": created_raffles_button,
            "active_raffles_button": active_raffles_button,
            "completed_raffles_button": completed_raffles_button}
