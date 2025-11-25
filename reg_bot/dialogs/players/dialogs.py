from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format

from .getters import (getter_player_home,
                      getter_player_raffle)
from reg_bot.states import PlayerState

player_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Group(Select(text=Format("{item.title}"),
                     id="select_play_raffle",
                     item_id_getter=lambda x: x.id,
                     items="play_raffles"),
              width=1),
        getter=getter_player_home,
        state=PlayerState.home
    ),
    Window(
        Format("{text}"),
        getter=getter_player_raffle,
        state=PlayerState.raffle
    )
)
