from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Format

from bot.states import CompletedRaffleState
from .getters import (getter_completed_raffle_home,
                      getter_completed_raffle)
from .handlers import (back_to_user_home,
                       completed_raffle,
                       back_to_raffles)

completed_raffle_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Group(Select(text=Format("{item.title}"),
                     id="select_completed_raffle",
                     item_id_getter=lambda x: x.id,
                     items="raffle_buttons",
                     on_click=completed_raffle),
              width=1),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=back_to_user_home),
        getter=getter_completed_raffle_home,
        state=CompletedRaffleState.home
    ),
    Window(
        Format("{raffle_text}"),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=back_to_raffles),
        getter=getter_completed_raffle,
        state=CompletedRaffleState.raffle
    )
)
