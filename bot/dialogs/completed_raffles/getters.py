from aiogram.types import User
from aiogram_dialog import DialogManager
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id, get_raffle_by_id


async def getter_completed_raffle_home(i18n: TranslatorHub,
                                       event_from_user: User,
                                       **kwargs) -> dict[str, str | list]:
    user = await get_user_by_id(event_from_user.id)
    raffles = user.completed_raffles

    return {"home_text": i18n.completed.raffle.home.text(),
            "back_button": i18n.back.button(),
            "raffle_buttons": raffles}


async def getter_completed_raffle(i18n: TranslatorHub,
                                  dialog_manager: DialogManager,
                                  **kwargs) -> dict[str, str]:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    channels_text = "\n".join([f"• {ch.title}" for ch in raffle.channels])

    raffle_text = i18n.completed.raffle.text(
        title=raffle.title,
        channels=channels_text,
        players_count=len(raffle.raffle_players),
        winners="Позже..."
    )


    return {"back_button": i18n.back.button(),
            "raffle_text": raffle_text}
