from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from .getters import getter_channel_home
from bot.states import ChannelState
from .handlers import channel_back_to_home_menu

channel_dialog = Dialog(
    Window(
        Format("{home_text}"),
        Button(text=Format("{add_channel_button}"),
               id="add_channel_button",
               on_click=None),
        Button(text=Format("{back_button}"),
               id="back_button_to_home_menu",
               on_click=channel_back_to_home_menu),
        getter=getter_channel_home,
        state=ChannelState.home,
    )
)
