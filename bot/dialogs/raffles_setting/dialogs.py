from aiogram_dialog import Dialog,Window
from aiogram_dialog.widgets.text import Format

from .getters import getter_raffle_setting_home
from bot.states import RaffleSettingState

raffle_settings_dialog = Dialog(
    Window(
        Format("{home_text}"),
        getter=getter_raffle_setting_home,
        state=RaffleSettingState.home
    )
)