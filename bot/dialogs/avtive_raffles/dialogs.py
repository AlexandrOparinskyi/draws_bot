from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Row
from aiogram_dialog.widgets.text import Format

from bot.states import ActiveRaffleState
from .getters import (getter_active_raffle_home,
                      getter_active_raffle,
                      getter_finish_confirm,
                      getter_subscribe_channels)
from .handlers import (back_to_user_home,
                       active_raffle_select_raffle,
                       active_raffle_back_to_home,
                       active_raffle_back_to_raffle,
                       active_raffle_confirm_finish,
                       active_raffle_sub_channels,
                       active_raffle_channel_inst,
                       active_raffle_finish)
from ..created_raffles.getters import getter_raffle_add_channels_instr
from ..created_raffles.handlers import created_raffle_toggle_channel

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
        Button(text=Format("{sub_channels_button}"),
               id="sub_channels_button",
               on_click=active_raffle_sub_channels),
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
    ),
    Window(
        Format("{sub_text}"),
        Button(text=Format("{add_channel_button}"),
               id="add_channel_button",
               on_click=active_raffle_channel_inst),
        Group(Select(text=Format("{item[0]}"),
                     id="enable_subscribe_channel",
                     item_id_getter=lambda x: x[1],
                     items="channels",
                     on_click=created_raffle_toggle_channel),
              width=1),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=active_raffle_back_to_raffle),
        getter=getter_subscribe_channels,
        state=ActiveRaffleState.sub_channels
    ),
    Window(
        Format("{instruction_text}"),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=active_raffle_sub_channels),
        getter=getter_raffle_add_channels_instr,
        state=ActiveRaffleState.add_channel_instruction
    )
)
