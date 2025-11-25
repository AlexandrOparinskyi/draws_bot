from aiogram.types import User
from aiogram_dialog import DialogManager
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id


async def getter_player_home(i18n: TranslatorHub,
                             event_from_user: User,
                             **kwargs) -> dict[str, str | list]:
    user = await get_user_by_id(event_from_user.id)

    if user.raffle_players:
        home_text = i18n.player.home.text()
        play_raffles = user.play_raffles
    else:
        home_text = i18n.player.raffle.empty()
        play_raffles = []

    return {"home_text": home_text,
            "play_raffles": play_raffles}


async def getter_player_raffle(i18n: TranslatorHub,
                               dialog_manager: DialogManager,
                               **kwargs) -> dict[str, str]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    return {"text": "Okay"}
