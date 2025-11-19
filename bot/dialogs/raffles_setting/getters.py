from aiogram_dialog import DialogManager
from fluentogram import TranslatorHub

from bot.utils import get_raffle_by_id


async def getter_raffle_setting_home(i18n: TranslatorHub,
                                     dialog_manager: DialogManager,
                                     **kwargs) -> dict[str, str]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)

    print(raffle)

    return {"home_text": i18n.raffle.setting.home.text()}
