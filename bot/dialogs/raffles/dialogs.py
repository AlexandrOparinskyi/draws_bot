from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Group, Select, Button
from aiogram_dialog.widgets.text import Format

from bot.states import RaffleState
from .getters import (getter_raffle_title,
                      getter_raffle_description,
                      getter_raffle_end_date,
                      getter_raffle_winners_count,
                      getter_raffle_ref_system,
                      getter_raffle_media)
from .handlers import (raffle_enter_title,
                       raffle_error_format,
                       raffle_enter_description,
                       raffle_enter_end_date,
                       raffle_enter_winners_count,
                       raffle_select_winners_count,
                       raffle_skip_load_media,
                       raffle_load_media,
                       raffle_select_ref_system)

raffle_dialog = Dialog(
    Window(
        Format("{title_text}"),
        MessageInput(func=raffle_enter_title,
                     content_types=ContentType.TEXT),
        MessageInput(func=raffle_error_format,
                     content_types=ContentType.ANY),
        getter=getter_raffle_title,
        state=RaffleState.title
    ),
    Window(
        Format("{description_text}"),
        MessageInput(func=raffle_enter_description,
                     content_types=ContentType.TEXT),
        MessageInput(func=raffle_error_format,
                     content_types=ContentType.ANY),
        getter=getter_raffle_description,
        state=RaffleState.description
    ),
    Window(
        Format("{media_text}"),
        MessageInput(func=raffle_load_media,
                     content_types=(ContentType.TEXT,
                                    ContentType.PHOTO,
                                    ContentType.VIDEO)),
        MessageInput(func=raffle_error_format,
                     content_types=ContentType.ANY),
        Button(text=Format("{skip_button}"),
               id="raffle_skip_load_media",
               on_click=raffle_skip_load_media),
        getter=getter_raffle_media,
        state=RaffleState.media
    ),
    Window(
        Format("{end_date_text}"),
        MessageInput(func=raffle_enter_end_date,
                     content_types=ContentType.TEXT),
        MessageInput(func=raffle_error_format,
                     content_types=ContentType.ANY),
        getter=getter_raffle_end_date,
        state=RaffleState.end_date
    ),
    Window(
        Format("{winners_count_text}"),
        MessageInput(func=raffle_enter_winners_count,
                     content_types=ContentType.TEXT),
        MessageInput(func=raffle_error_format,
                     content_types=ContentType.ANY),
        Group(Select(text=Format("{item}"),
                     id="select_winners_count",
                     item_id_getter=lambda x: x,
                     items="buttons",
                     on_click=raffle_select_winners_count),
              width=3),
        getter=getter_raffle_winners_count,
        state=RaffleState.winners_count
    ),
    Window(
        Format("{ref_system_text}"),
        Button(text=Format("{yes_button}"),
               id="enable_ref_system",
               on_click=raffle_select_ref_system),
        Button(text=Format("{no_button}"),
               id="disable_ref_system",
               on_click=raffle_select_ref_system),
        getter=getter_raffle_ref_system,
        state=RaffleState.ref_system
    )
)
