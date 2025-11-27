from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from fluentogram import TranslatorHub

from bot.utils import (get_user_by_id,
                       get_raffle_by_id,
                       edit_selected_param)
from config import Config
from reg_bot.utils import (get_channels_for_subscribe,
                           transfer_file_if_needed,
                           get_referrals_count)


async def getter_player_home(i18n: TranslatorHub,
                             event_from_user: User,
                             **kwargs) -> dict[str, str | list]:
    user = await get_user_by_id(event_from_user.id)

    if user.play_raffles:
        home_text = i18n.player.home.text()
        play_raffles = user.play_raffles
    else:
        home_text = i18n.player.raffle.empty()
        play_raffles = []

    return {"home_text": home_text,
            "play_raffles": play_raffles}


async def getter_player_raffle(i18n: TranslatorHub,
                               dialog_manager: DialogManager,
                               event_from_user: User,
                               **kwargs) -> dict[str, str | None]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)

    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")
    friends_count = await get_referrals_count(event_from_user.id)

    raffle_text = i18n.player.raffle.text(
        title=raffle.title,
        description=raffle.description,
        date=date, time=time,
        friends_count=friends_count
    )

    media = None
    if raffle.photo_id:
        if raffle.player_photo_id:
            media = MediaAttachment(
                ContentType.PHOTO,
                raffle.player_photo_id
            )
        else:
            check_bot: Bot = dialog_manager.middleware_data.get("check_bot")
            bot: Bot = dialog_manager.middleware_data.get("bot")
            config: Config = dialog_manager.middleware_data.get("config")

            new_file_id = await transfer_file_if_needed(
                raffle.photo_id,
                check_bot,
                bot,
                config,
                "photo"
            )
            if new_file_id:
                await edit_selected_param("player_photo_id",
                                          new_file_id,
                                          raffle_id)
                media = MediaAttachment(
                    ContentType.PHOTO,
                    new_file_id
                )

    elif raffle.video_id:
        if raffle.player_video_id:
            media = MediaAttachment(
                ContentType.VIDEO,
                raffle.player_video_id
            )
        else:
            check_bot: Bot = dialog_manager.middleware_data.get("check_bot")
            bot: Bot = dialog_manager.middleware_data.get("bot")
            config: Config = dialog_manager.middleware_data.get("config")

            new_file_id = await transfer_file_if_needed(
                raffle.video_id,
                check_bot,
                bot,
                config,
                "video"
            )
            if new_file_id:
                await edit_selected_param("player_video_id",
                                          new_file_id,
                                          raffle_id)
                media = MediaAttachment(
                    ContentType.VIDEO,
                    new_file_id
                )

    invite_button = ""
    if raffle.ref_system:
        invite_button = i18n.invite.friend()

    return {"raffle_text": raffle_text,
            "media": media,
            "back_button": i18n.back.button(),
            "invite_button": invite_button}


async def getter_player_check_sub(i18n: TranslatorHub,
                                  dialog_manager: DialogManager,
                                  config: Config,
                                  check_bot: Bot,
                                  **kwargs) -> dict[str, str | list]:
    if dialog_manager.start_data:
        dialog_manager.dialog_data.update(**dialog_manager.start_data)
        dialog_manager.start_data.clear()

    raffle_id = int(dialog_manager.dialog_data.get("raffle_id"))
    raffle = await get_raffle_by_id(raffle_id)
    unsub_channels = dialog_manager.dialog_data.get("channels")
    channels = await get_channels_for_subscribe(unsub_channels,
                                                raffle_id)
    channels_text = "\n".join(f"<b>• {ch.title}</b>"
                              for ch in raffle.channels)

    if not dialog_manager.dialog_data.get("main_channel"):
        chat = await check_bot.get_chat(config.tg_bot.channel)
        channels.append(config.tg_bot.channel)
        channels_text += f"\n<b>• {chat.title}</b>"

    text = i18n.player.subscribe.text(
        channels=channels_text
    )

    channel_widget = []
    for channel in channels:
        chat = await check_bot.get_chat(channel)
        if chat.username:
            url = f"https://t.me/{chat.username}"
        else:
            invite = await check_bot.create_chat_invite_link(chat.id,
                                                             member_limit=1)
            url = invite.invite_link

        channel_widget.append({"title": chat.title, "url": url, "id": chat.id})

    return {"check_subscribe_text": text,
            "channel_widget": channel_widget,
            "confirm_button": i18n.player.subscribe.confirm()}
