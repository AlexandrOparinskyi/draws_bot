from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from .getters import (getter_channel_home,
                      getter_channel_instruction)
from bot.states import ChannelState
from .handlers import (channel_back_to_home_menu,
                       channel_back_to_channels,
                       channel_instruction)

channel_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Button(text=Format("{add_channel_button}"),
               id="add_channel_button",
               on_click=channel_instruction),
        Button(text=Format("{back_button}"),
               id="back_button_to_home_menu",
               on_click=channel_back_to_home_menu),
        getter=getter_channel_home,
        state=ChannelState.home,
    ),
    Window(
        Format("{instruction_text}"),
        Button(text=Format("{back_button}"),
               id="back_button_to_channels",
               on_click=channel_back_to_channels),
        getter=getter_channel_instruction,
        state=ChannelState.instruction
    )
)
