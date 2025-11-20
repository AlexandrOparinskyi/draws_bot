from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Row
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format

from bot.states import CreatedRaffleState
from .getters import (getter_created_raffle_home,
                      getter_created_raffle_raffle,
                      getter_create_raffle_confirm_delete,
                      getter_created_raffle_preview)
from .handlers import (created_raffle_back_to_start,
                       created_raffle_select_raffle,
                       created_raffle_back_to_select,
                       created_raffle_back_to_raffle,
                       created_raffle_delete_yes,
                       created_raffle_delete_raffle,
                       created_raffle_preview,
                       created_raffle_preview_link)

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
        Row(Button(text=Format("{edit_button}"),
                   id="edit_button",
                   on_click=None),
            Button(text=Format("{preview_button}"),
                   id="preview_button",
                   on_click=created_raffle_preview)),
        Button(text=Format("{subscribe_channels_button}"),
               id="subscribe_channels_button",
               on_click=None),
        Button(text=Format("{public_channels_button}"),
               id="public_channels_button",
               on_click=None),
        Row(Button(text=Format("{start_raffle}"),
                   id="start_raffle",
                   on_click=None),
            Button(text=Format("{delete_raffle}"),
                   id="delete_raffle",
                   on_click=created_raffle_delete_raffle)),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=created_raffle_back_to_select),
        getter=getter_created_raffle_raffle,
        state=CreatedRaffleState.raffle
    ),
    Window(
        Format("{confirm_delete_text}"),
        Row(Button(text=Format("{yes_button}"),
                   id="delete_raffle_yes_button",
                   on_click=created_raffle_delete_yes),
            Button(text=Format("{no_button}"),
                   id="delete_raffle_no_button",
                   on_click=created_raffle_back_to_raffle)),
        getter=getter_create_raffle_confirm_delete,
        state=CreatedRaffleState.confirm_delete
    ),
    Window(
        Format("{raffle_text}"),
        DynamicMedia("media"),
        Button(text=Format("{title_button}"),
               id="check_raffle_button",
               on_click=created_raffle_preview_link),
        Button(text=Format("{back_button}"),
               id="back_button",
               on_click=created_raffle_back_to_raffle),
        getter=getter_created_raffle_preview,
        state=CreatedRaffleState.preview
    )
)
