from aiogram.types import User
from aiogram_dialog import DialogManager
from fluentogram import TranslatorHub

from bot.utils import get_user_by_id, get_raffle_by_id, get_user_active_channels


async def getter_active_raffle_home(i18n: TranslatorHub,
                                    event_from_user: User,
                                    **kwargs) -> dict[str, str | list]:
    user = await get_user_by_id(event_from_user.id)

    return {"home_text": i18n.active.raffle.home.text(),
            "back_button": i18n.back.button(),
            "raffle_buttons": user.active_raffles}


async def getter_active_raffle(i18n: TranslatorHub,
                               dialog_manager: DialogManager,
                               **kwargs) -> dict[str, str]:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")
    ref_system = "✔️ Включена" if raffle.ref_system else "❌ Выключена"
    channels = "\n".join([f"• <b>{ch.title}</b>" for ch in raffle.channels])

    raffle_text = i18n.active.raffle.text(
        channels=channels,
        title=raffle.title,
        date=date, time=time,
        ref_system=ref_system,
        winners_count=raffle.winners_count,
        players=len(raffle.raffle_players)
    )

    return {"raffle_text": raffle_text,
            "back_button": i18n.back.button(),
            "finish_button": i18n.raffle.finish.button(),
            "sub_channels_button": i18n.subscribe.channels.button()}


async def getter_finish_confirm(i18n: TranslatorHub,
                                dialog_manager: DialogManager,
                                **kwargs) -> dict[str, str]:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    confirm_text = i18n.raffle.finish.text(title=raffle.title,
                                           date=raffle.end_date,
                                           players=len(raffle.raffle_players))

    return {"confirm_text": confirm_text,
            "yes_button": i18n.finish.yes.button(),
            "no_button": i18n.finish.no.button()}


async def getter_subscribe_channels(i18n: TranslatorHub,
                                    event_from_user: User,
                                    dialog_manager: DialogManager,
                                    **kwargs) -> dict[str, str | list]:
    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    channels = await get_user_active_channels(raffle_id,
                                              event_from_user.id)

    return {"sub_text": i18n.created.channel.instruction(),
            "channels": channels,
            "back_button": i18n.back.button(),
            "add_channel_button": i18n.channel.add.button()}
