from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format

from bot.states import CreatedRaffleState
from .getters import (getter_created_raffle_home,
                      getter_created_raffle_raffle)
from .handlers import (created_raffle_back_to_start,
                       created_raffle_select_raffle,
                       created_raffle_back_to_select)

created_raffles_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Group(Select(text=Format("{item.title}"),
                     id="select_raffle",
                     item_id_getter=lambda x: x.id,
                     items="raffle_buttons",
                     on_click=created_raffle_select_raffle),
              width=1),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=created_raffle_back_to_start),
        getter=getter_created_raffle_home,
        state=CreatedRaffleState.home
    ),
    Window(
        Format("{raffle_text}"),
        DynamicMedia("media"),
        Button(text=Format("{edit_button}"),
               id="edit_button",
               on_click=None),
        Button(text=Format("{subscribe_channels_button}"),
               id="subscribe_channels_button",
               on_click=None),
        Button(text=Format("{public_channels_button}"),
               id="public_channels_button",
               on_click=None),
        Button(text=Format("{start_raffle}"),
               id="start_raffle",
               on_click=None),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=created_raffle_back_to_select),
        getter=getter_created_raffle_raffle,
        state=CreatedRaffleState.raffle
    )
)
