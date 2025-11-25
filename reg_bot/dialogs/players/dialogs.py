from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Select, Button, ListGroup, Url
from aiogram_dialog.widgets.text import Format

from .getters import (getter_player_home,
                      getter_player_raffle,
                      getter_player_check_sub)
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
    ),
    Window(
        Format("{check_subscribe_text}"),
        ListGroup(Url(text=Format("{item[title]}"),
                      url=Format("{item[url]}")),
                  id="select_unsubscribe_channel",
                  item_id_getter=lambda x: x["id"],
                  items="channel_widget"),
        Button(text=Format("{confirm_button}"),
               id="confirm_button",
               on_click=None),
        getter=getter_player_check_sub,
        state=PlayerState.check_subscribe
    )
)
