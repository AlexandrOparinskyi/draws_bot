from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Row
from aiogram_dialog.widgets.text import Format

from bot.states import ActiveRaffleState
from .getters import (getter_active_raffle_home,
                      getter_active_raffle,
                      getter_finish_confirm)
from .handlers import (back_to_user_home,
                       active_raffle_select_raffle,
                       active_raffle_back_to_home,
                       active_raffle_back_to_raffle,
                       active_raffle_confirm_finish,
                       active_raffle_finish)

active_raffle_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Group(Select(text=Format("{item.title}"),
                     id="select_active_raffle",
                     item_id_getter=lambda x: x.id,
                     items="raffle_buttons",
                     on_click=active_raffle_select_raffle),
              width=1),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=back_to_user_home),
        getter=getter_active_raffle_home,
        state=ActiveRaffleState.home
    ),
    Window(
        Format("{raffle_text}"),
        Button(text=Format("{finish_button}"),
               id="finish_button",
               on_click=active_raffle_confirm_finish),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=active_raffle_back_to_home),
        getter=getter_active_raffle,
        state=ActiveRaffleState.raffle
    ),
    Window(
        Format("{confirm_text}"),
        Row(Button(text=Format("{yes_button}"),
                   id="yes_button",
                   on_click=active_raffle_finish),
            Button(text=Format("{no_button}"),
                   id="no_button",
                   on_click=active_raffle_back_to_raffle),
            ),
        getter=getter_finish_confirm,
        state=ActiveRaffleState.finish_confirm
    )
)
