from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Select, Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format

from .getters import (getter_edit_raffle_changes,
                      getter_edit_raffle_change_param)
from .handlers import (edit_raffle_edit_param,
                       edit_raffle_toggle_ref_system,
                       edit_raffle_back_to_raffle,
                       edit_raffle_back_to_changes,
                       edit_raffle_select_param)
from bot.states import ChangeRaffleState

edit_raffle_dialog = Dialog(
Window(
        Format("{changes_text}"),
        DynamicMedia("media"),
        Group(Select(text=Format("{item[0]}"),
                     id="edit_raffle_data",
                     item_id_getter=lambda x: x[1],
                     items="edit_buttons",
                     on_click=edit_raffle_edit_param),
              width=2),
        Button(text=Format("{ref_system_button}"),
               id="ref_system_button",
               on_click=edit_raffle_toggle_ref_system),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=edit_raffle_back_to_raffle),
        getter=getter_edit_raffle_changes,
        state=ChangeRaffleState.changes,
    ),
    Window(
        Format("{changed_text}"),
        Group(Select(text=Format("{item[0]}"),
                     id="change_raffle_part",
                     item_id_getter=lambda x: x[1],
                     items="buttons",
                     on_click=edit_raffle_select_param),
              width=3),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=edit_raffle_back_to_changes),
        getter=getter_edit_raffle_change_param,
        state=ChangeRaffleState.change_param
    )
)