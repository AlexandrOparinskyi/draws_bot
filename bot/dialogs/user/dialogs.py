from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from bot.states import UserState
from .getters import getter_user_home
from .handlers import (user_create_raffle,
                       user_created_raffles, user_channels)

user_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Button(text=Format("{new_raffle_button}"),
               id="new_raffle_button",
               on_click=user_create_raffle),
        Button(text=Format("{created_raffles_button}"),
               id="created_raffles_button",
               on_click=user_created_raffles),
        Button(text=Format("{active_raffles_button}"),
               id="active_raffles_button",
               on_click=None),
        Button(text=Format("{completed_raffles_button}"),
               id="completed_raffles_button",
               on_click=None),
        Button(text=Format("{channels_button}"),
               id="channels_button",
               on_click=user_channels),
        getter=getter_user_home,
        state=UserState.home
    )
)
